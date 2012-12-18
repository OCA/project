# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Vincent Renaville, ported by Joel Grand-Guillaume
#    Copyright 2010-2012 Camptocamp SA
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
##############################################################################

from openerp.osv import orm, fields


class AccountHoursBlock(orm.Model):
    _name = "account.hours.block"

    def _get_last_action(self, cr, uid, ids, name, arg, context=None):
        """ Return the last analytic line date for an invoice"""
        res = {}
        for block in self.browse(cr, uid, ids, context=context):
            cr.execute("SELECT max(al.date) FROM account_analytic_line AS al"
                       " WHERE al.invoice_id = %s", (block.invoice_id.id,))
            fetch_res = cr.fetchone()
            res[block.id] = fetch_res[0] if fetch_res else False
        return res

    def _compute_hours(self, cr, uid, ids, fields, args, context=None):
        """Return a dict of [id][fields]"""
        if isinstance(ids, (int, long)):
            ids = [ids]
        result = {}
        aal_obj = self.pool.get('account.analytic.line')
        for block in self.browse(cr, uid, ids, context=context):
            result[block.id] = {'amount_hours_block': 0.0,
                                'amount_hours_block_done': 0.0}
            # Compute hours bought
            for line in block.invoice_id.invoice_line:
                hours_bought = 0.0
                if line.product_id:
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
                       "AND al.invoice_id = %s", (block.invoice_id.id,))
            res_line_ids = cr.fetchall()
            line_ids = [l[0] for l in res_line_ids] if res_line_ids else []
            for line in aal_obj.browse(cr, uid, line_ids, context=context):
                factor = 1.0
                if line.product_uom_id and line.product_uom_id.factor != 0.0:
                    factor = line.product_uom_id.factor
                factor_invoicing = 1.0
                if line.to_invoice and line.to_invoice.factor != 0.0:
                    factor_invoicing = 1.0 - line.to_invoice.factor / 100
                hours_used += ((line.unit_amount / factor) * factor_invoicing)
            result[block.id]['amount_hours_block_done'] = hours_used
        return result

    def _compute_amount(self, cr, uid, ids, fields, args, context=None):
        if context is None:
            context = {}
        result = {}
        aal_obj = self.pool.get('account.analytic.line')
        pricelist_obj = self.pool.get('product.pricelist')
        for block in self.browse(cr, uid, ids, context=context):
            result[block.id] = {'amount_hours_block': 0.0,
                                'amount_hours_block_done': 0.0}

            # Compute amount bought
            for line in block.invoice_id.invoice_line:
                amount_bought = 0.0
                if line.product_id:
                    ## We will now calculate the product_quantity
                    factor = line.uos_id.factor
                    if factor == 0.0:
                        factor = 1.0
                    amount = line.quantity * line.price_unit
                    amount_bought += (amount / factor)
                result[block.id]['amount_hours_block'] += amount_bought

            # Compute total amount
            # Get ids of analytic line generated from timesheet associated to current block
            cr.execute("SELECT al.id FROM account_analytic_line AS al,"
                       " account_analytic_journal AS aj"
                       " WHERE aj.id = al.journal_id"
                       "  AND aj.type='general'"
                       "  AND al.invoice_id = %s", (block.invoice_id.id,))
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
                        line.product_id.id,
                        line.unit_amount or 1.0,
                        line.account_id.partner_id.id or False,
                        ctx)[line.account_id.pricelist_id.id]
                total_amount += amount * line.unit_amount * factor_invoicing
            result[block.id]['amount_hours_block_done'] += total_amount

        return result

    def _compute(self, cr, uid, ids, fields, args, context=None):
        result = {}
        block_per_types = {}
        for block in self.browse(cr, uid, ids, context=context):
            block_per_types.setdefault(block.type, []).append(block.id)

        for block_type in block_per_types:
            if block_type:
                func = getattr(self, "_compute_%s" % block_type)
                result.update(func(cr, uid, ids, fields, args, context=context))

        for block in result:
            result[block]['amount_hours_block_delta'] = \
                result[block]['amount_hours_block'] - \
                result[block]['amount_hours_block_done']
        return result

    _columns = {
        'amount_hours_block': fields.function(
            _compute,
            type='float',
            string='Quantity / Amount bought',
            store=True,
            multi='amount_hours_block_delta',
            help="Amount bought by the customer. "
                 "This amount is expressed in the base Unit of Measure "
                 "(factor=1.0)"),
        'amount_hours_block_done': fields.function(
            _compute,
            type='float',
            string='Quantity / Amount used',
            store=True,
            multi='amount_hours_block_delta',
            help="Amount done by the staff. "
                 "This amount is expressed in the base Unit of Measure "
                 "(factor=1.0)"),
        'amount_hours_block_delta': fields.function(
            _compute,
            type='float',
            string='Difference',
            store=True,
            multi='amount_hours_block_delta',
            help="Difference between bought and used. "
                 "This amount is expressed in the base Unit of Measure "
                 "(factor=1.0)"),
        'last_action_date': fields.function(
            _get_last_action,
            type='date',
            string='Last action date',
            help="Date of the last analytic line linked to the invoice "
                 "related to this block hours."),
        'close_date': fields.date('Closed Date'),
        'invoice_id': fields.many2one(
            'account.invoice',
            'Invoice',
            ondelete='cascade',
            required=True),
        'type': fields.selection(
            [('hours', 'Hours'),
             ('amount', 'Amount')],
            string='Type of Block',
            required=True,
            help="The block is based on the quantity of hours "
                 "or on the amount."),

        # Invoices related infos
        'date_invoice': fields.related(
            'invoice_id', 'date_invoice',
            type="date",
            string="Invoice Date",
            store=True,
            readonly=True),
        'user_id': fields.related(
            'invoice_id', 'user_id',
            type="many2one",
            relation="res.users",
            string="Salesman",
            store=True,
            readonly=True),
        'partner_id': fields.related(
            'invoice_id', 'partner_id',
            type="many2one",
            relation="res.partner",
            string="Partner",
            store=True,
            readonly=True),
        'name': fields.related(
            'invoice_id', 'name',
            type="char",
            size=64,
            string="Description",
            store=True,
            readonly=True),
        'number': fields.related(
            'invoice_id', 'number',
            type="char",
            size=64,
            string="Number",
            store=True,
            readonly=True),
        'journal_id': fields.related(
            'invoice_id', 'journal_id',
            type="many2one",
            relation="account.journal",
            string="Journal",
            store=True,
            readonly=True),
        'period_id': fields.related(
            'invoice_id', 'period_id',
            type="many2one",
            relation="account.period",
            string="Period",
            store=True,
            readonly=True),
        'company_id': fields.related(
            'invoice_id', 'company_id',
            type="many2one",
            relation="res.company",
            string="Company",
            store=True,
            readonly=True),
        'currency_id': fields.related(
            'invoice_id', 'currency_id',
            type="many2one",
            relation="res.currency",
            string="Currency",
            store=True,
            readonly=True),
        'residual': fields.related(
            'invoice_id', 'residual',
            type="float",
            string="Residual",
            store=True,
            readonly=True),
        'amount_total': fields.related(
            'invoice_id', 'amount_total',
            type="float",
            string="Total",
            store=True,
            readonly=True),
        'state': fields.related(
            'invoice_id', 'state',
            type='selection',
            selection=[
                ('draft', 'Draft'),
                ('proforma', 'Pro-forma'),
                ('proforma2', 'Pro-forma'),
                ('open', 'Open'),
                ('paid', 'Paid'),
                ('cancel', 'Cancelled'),
            ],
            string='State',
            readonly=True,
            store=True),
    }


############################################################################
## Add hours blocks on invoice
############################################################################
class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'account_hours_block_ids': fields.one2many(
            'account.hours.block',
            'invoice_id',
            string='Hours Block')
    }
