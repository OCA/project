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
    _inherit = ['mail.thread']

    def _get_last_action(self, cr, uid, ids, name, arg, context=None):
        """ Return the last analytic line date for an invoice"""
        res = {}
        for block in self.browse(cr, uid, ids, context=context):
            cr.execute("SELECT max(al.date) FROM account_analytic_line AS al"
                       " WHERE al.invoice_id = %s "
                       " AND al.account_id = %s",
                       (block.invoice_id.id, block.account_analytic_id.id))
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
                block_analytic_id = block.account_analytic_id.id
                line_account_analytic_id = line.account_analytic_id.id
                if line.product_id and \
                        line.product_id.is_in_hours_block and \
                        block_analytic_id == line_account_analytic_id:
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
                result.update(func(cr, uid, ids,
                                   fields, args, context=context))

        for block in result:
            result[block]['amount_hours_block_delta'] = \
                result[block]['amount_hours_block'] - \
                result[block]['amount_hours_block_done']
        return result

    def _get_analytic_line(self, cr, uid, ids, context=None):
        invoice_ids = []
        an_lines_obj = self.pool.get('account.analytic.line')
        block_obj = self.pool.get('account.hours.block')
        for line in an_lines_obj.browse(cr, uid, ids, context=context):
            if line.invoice_id:
                invoice_ids.append(line.invoice_id.id)
        return block_obj.search(
            cr, uid, [('invoice_id', 'in', invoice_ids)], context=context)

    def _get_invoice(self, cr, uid, ids, context=None):
        block_ids = set()
        inv_obj = self.pool.get('account.invoice')
        for invoice in inv_obj.browse(cr, uid, ids, context=context):
            block_ids.update([inv.id for inv
                              in invoice.account_hours_block_ids])
        return list(block_ids)

    def _get_invoice_line(self, cr, uid, ids, context=None):
        invoice_ids = set()
        line_obj = self.pool.get('account.invoice.line')
        block_obj = self.pool.get('account.hours.block')
        for line in line_obj.browse(cr, uid, ids, context=context):
            if line.invoice_id:
                invoice_ids.add(line.invoice_id.id)
        return block_obj._get_invoice(
            cr, uid, list(invoice_ids), context=context)

    def action_send_block(self, cr, uid, ids, context=None):
        """Open a form to send by email. Return an action dict."""

        assert len(ids) == 1, '''\
            This option should only be used for a single ID at a time.'''

        ir_model_data = self.pool.get('ir.model.data')

        try:
            template_id = ir_model_data.get_object_reference(
                cr, uid, 'analytic_hours_block', 'email_template_hours_block'
            )[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data.get_object_reference(
                cr, uid, 'mail', 'email_compose_message_wizard_form'
            )[1]
        except ValueError:
            compose_form_id = False

        ctx = {
            'default_model': self._name,
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    _recompute_triggers = {
        'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                ['invoice_id', 'type',
                                 'account_analytic_id'], 10),
        'account.invoice': (_get_invoice, ['analytic_line_ids'], 10),
        'account.analytic.line': (
            _get_analytic_line,
            ['product_uom_id', 'unit_amount', 'to_invoice',
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
        'account_analytic_id': fields.many2one(
            'account.analytic.account',
            'Account analytic',
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
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['date_invoice'], 10),
            },
            readonly=True),
        'user_id': fields.related(
            'invoice_id', 'user_id',
            type="many2one",
            relation="res.users",
            string="Salesman",
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['user_id'], 10),
            },
            readonly=True),
        'partner_id': fields.related(
            'invoice_id', 'partner_id',
            type="many2one",
            relation="res.partner",
            string="Partner",
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['partner_id'], 10),
            },
            readonly=True),
        'name': fields.related(
            'invoice_id', 'name',
            type="char",
            string="Description",
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['name'], 10),
            },
            readonly=True),
        'number': fields.related(
            'invoice_id', 'number',
            type="char",
            string="Number",
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['number'], 10),
            },
            readonly=True),
        'journal_id': fields.related(
            'invoice_id', 'journal_id',
            type="many2one",
            relation="account.journal",
            string="Journal",
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['journal_id'], 10),
            },
            readonly=True),
        'period_id': fields.related(
            'invoice_id', 'period_id',
            type="many2one",
            relation="account.period",
            string="Period",
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['period_id'], 10),
            },
            readonly=True),
        'company_id': fields.related(
            'invoice_id', 'company_id',
            type="many2one",
            relation="res.company",
            string="Company",
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['company_id'], 10),
            },
            readonly=True),
        'currency_id': fields.related(
            'invoice_id', 'currency_id',
            type="many2one",
            relation="res.currency",
            string="Currency",
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['currency_id'], 10),
            },
            readonly=True),
        'residual': fields.related(
            'invoice_id', 'residual',
            type="float",
            string="Residual",
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['residual'], 10),
            },
            readonly=True),
        'amount_total': fields.related(
            'invoice_id', 'amount_total',
            type="float",
            string="Total",
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['amount_total'], 10),
            },
            readonly=True),
        'department_id': fields.related(
            'invoice_id', 'department_id',
            type='many2one',
            relation='hr.department',
            string='Department',
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['department_id'], 10),
            },
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
            store={
                'account.hours.block': (lambda self, cr, uid, ids, c=None: ids,
                                        ['invoice_id'], 10),
                'account.invoice': (_get_invoice, ['state'], 10),
            }),
    }


############################################################################
# Add hours blocks on invoice
############################################################################
class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'account_hours_block_ids': fields.one2many(
            'account.hours.block',
            'invoice_id',
            string='Hours Block')
    }
