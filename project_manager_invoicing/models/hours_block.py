# -*- coding: utf-8 -*-
#
#    Author: Denis Leemann
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from openerp.osv import orm, fields


class AccountHoursBlock(orm.Model):
    # The goal of this rewrite is to make the update of calculation
    # with invoiced_hours instead of invoiced_hours
    _inherit = "account.hours.block"

    def _compute(self, cr, uid, ids, fields, args, context=None):
        # Just to be sure it is called right
        # return super(AccountHoursBlock, self)._compute(cr, uid, ids, fields,
        # args, context=context)
        result = {}
        block_per_types = {}
        for block in self.browse(cr, uid, ids, context=context):
            block_per_types.setdefault(block.type, []).append(block.id)

        for block_type in block_per_types:
            if block_type:
                func = getattr(self, "_compute_%s" % block_type)
                result.update(func(cr, uid, ids,
                                   fields, args, context=context))

        for block in result:
            result[block]['amount_hours_block_delta'] = \
                result[block]['amount_hours_block'] - \
                result[block]['amount_hours_block_done']
        return result

    def _compute_hours(self, cr, uid, ids, fields, args, context=None):
        # Replaced line.unit_amount with line.invoiced_hours
        """Return a dict of [id][fields]"""
        if isinstance(ids, (int, long)):
            ids = [ids]
        result = {}
        aal_obj = self.pool['account.analytic.line']
        for block in self.browse(cr, uid, ids, context=context):
            result[block.id] = {'amount_hours_block': 0.0,
                                'amount_hours_block_done': 0.0}
            block_analytic_id = block.account_analytic_id.id
            # Compute hours bought
            for line in block.invoice_id.invoice_line:
                hours_bought = 0.0
                line_account_analytic_id = line.account_analytic_id.id
                if (line.product_id and
                        line.product_id.is_in_hours_block and
                        block_analytic_id == line_account_analytic_id):
                    # We will now calculate the product_quantity
                    factor = line.uos_id.factor
                    if factor == 0.0:
                        factor = 1.0
                    amount = line.quantity
                    hours_bought += (amount / factor)
                result[block.id]['amount_hours_block'] += hours_bought

            # Compute hours spent
            hours_used = 0.0
            # Get ids of analytic line generated from
            # timesheet associated to the current block
            cr.execute("SELECT al.id "
                       "FROM account_analytic_line AS al, "
                       "     account_analytic_journal AS aj "
                       "WHERE aj.id = al.journal_id "
                       "AND aj.type = 'general' "
                       "  AND al.invoice_id = %s"
                       "  AND al.account_id = %s",
                       (block.invoice_id.id, block.account_analytic_id.id))
            res_line_ids = cr.fetchall()
            line_ids = [l[0] for l in res_line_ids] if res_line_ids else []
            for line in aal_obj.browse(cr, uid, line_ids, context=context):
                factor = 1.0
                if line.product_uom_id and line.product_uom_id.factor != 0.0:
                    factor = line.product_uom_id.factor
                factor_invoicing = 1.0

                if line.to_invoice and line.to_invoice.factor != 0.0:
                    factor_invoicing = 1.0 - line.to_invoice.factor / 100
                hours_used += ((line.invoiced_hours / factor) * factor_invoicing)
            result[block.id]['amount_hours_block_done'] = hours_used
        return result

    def _compute_amount(self, cr, uid, ids, fields, args, context=None):
        if context is None:
            context = {}
        result = {}
        aal_obj = self.pool['account.analytic.line']
        pricelist_obj = self.pool['product.pricelist']
        for block in self.browse(cr, uid, ids, context=context):
            result[block.id] = {'amount_hours_block': 0.0,
                                'amount_hours_block_done': 0.0}

            # Compute amount bought
            for line in block.invoice_id.invoice_line:
                amount_bought = 0.0
                if line.product_id:
                    # We will now calculate the product_quantity
                    factor = line.uos_id.factor
                    if factor == 0.0:
                        factor = 1.0
                    amount = line.quantity * line.price_unit
                    amount_bought += (amount / factor)
                result[block.id]['amount_hours_block'] += amount_bought

            # Compute total amount
            # Get ids of analytic line generated from timesheet
            # associated to current block
            cr.execute("SELECT al.id FROM account_analytic_line AS al,"
                       " account_analytic_journal AS aj"
                       " WHERE aj.id = al.journal_id"
                       "  AND aj.type='general'"
                       "  AND al.invoice_id = %s"
                       "  AND al.account_id = %s",
                       (block.invoice_id.id, block.account_analytic_id.id))
            res_line_ids = cr.fetchall()
            line_ids = [l[0] for l in res_line_ids] if res_line_ids else []
            total_amount = 0.0
            for line in aal_obj.browse(cr, uid, line_ids, context=context):
                factor_invoicing = 1.0
                if line.to_invoice and line.to_invoice.factor != 0.0:
                    factor_invoicing = 1.0 - line.to_invoice.factor / 100

                ctx = dict(context, uom=line.product_uom_id.id)
                amount = pricelist_obj.price_get(
                    cr, uid,
                    [line.account_id.pricelist_id.id],
                    line.invoiced_product_id.id,
                    line.invoiced_hours or 1.0,
                    line.account_id.partner_id.id or False,
                    ctx)[line.account_id.pricelist_id.id]
                total_amount += amount * line.invoiced_hours * factor_invoicing
            result[block.id]['amount_hours_block_done'] += total_amount

        return result

    def _get_analytic_line(self, cr, uid, ids, context=None):
        invoice_ids = []
        an_lines_obj = self.pool['account.analytic.line']
        block_obj = self.pool['account.hours.block']
        for line in an_lines_obj.browse(cr, uid, ids, context=context):
            if line.invoice_id:
                invoice_ids.append(line.invoice_id.id)
        return block_obj.search(
            cr, uid, [('invoice_id', 'in', invoice_ids)], context=context)

    def _get_invoice(self, cr, uid, ids, context=None):
        block_ids = set()
        inv_obj = self.pool['account.invoice']
        for invoice in inv_obj.browse(cr, uid, ids, context=context):
            block_ids.update([inv.id for inv
                              in invoice.account_hours_block_ids])
        return list(block_ids)

    def _get_invoice_line(self, cr, uid, ids, context=None):
        invoice_ids = set()
        line_obj = self.pool['account.invoice.line']
        block_obj = self.pool['account.hours.block']
        for line in line_obj.browse(cr, uid, ids, context=context):
            if line.invoice_id:
                invoice_ids.add(line.invoice_id.id)
        return block_obj._get_invoice(
            cr, uid, list(invoice_ids), context=context)

    # TODO modification du prix si le produit envoyé est changé?
    # Pas utile, car une ligne doit être validée pour être associée
    # Pour changer une ligne, il est nécessaire de la dissocier (dans
    # le fonctionnement actuel(et voulu) du process)
    _recompute_triggers = {
        'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                ['invoice_id', 'type',
                                 'account_analytic_id'], 10),
        'account.invoice': (_get_invoice, ['analytic_line_ids'], 10),
        'account.analytic.line': (
            _get_analytic_line,
            ['product_uom_id', 'invoiced_hours', 'to_invoice',
             'invoice_id', 'account_id'],
            10),
        'account.invoice.line': (_get_invoice_line,
                                 ['account_analytic_id'], 10),
    }

    _columns = {
        'amount_hours_block': fields.function(
            _compute,
            type='float',
            string='Quantity / Amount bought',
            store=_recompute_triggers,
            multi='amount_hours_block_delta',
            help="Amount bought by the customer. "
                 "This amount is expressed in the base Unit of Measure "
                 "(factor=1.0)"),
        'amount_hours_block_done': fields.function(
            _compute,
            type='float',
            string='Quantity / Amount used',
            store=_recompute_triggers,
            multi='amount_hours_block_delta',
            help="Amount done by the staff. "
                 "This amount is expressed in the base Unit of Measure "
                 "(factor=1.0)"),
        'amount_hours_block_delta': fields.function(
            _compute,
            type='float',
            string='Difference',
            store=_recompute_triggers,
            multi='amount_hours_block_delta',
            help="Difference between bought and used. "
                 "This amount is expressed in the base Unit of Measure "
                 "(factor=1.0)"),
    }
