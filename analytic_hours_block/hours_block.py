# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Vincent Renaville, ported by Joel Grand-Guillaume, Damien Crier
#    Copyright 2010-2015 Camptocamp SA
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

from openerp import models, api, fields


class AccountHoursBlock(models.Model):
    _name = "account.hours.block"
    _inherit = ['mail.thread']

    @api.depends('invoice_id')
    def _get_last_action(self):
        """ Return the last analytic line date for an invoice"""
        res = {}
        for block in self:
            fetch_res = []
            if block.invoice_id:
                self.env.cr.execute("SELECT max(al.date) "
                                    "FROM account_analytic_line AS al "
                                    "WHERE al.invoice_id = %s",
                                    (block.invoice_id.id,))
                fetch_res = self.env.cr.fetchone()
            res[block.id] = fetch_res[0] if fetch_res else False
        return res

    @api.multi
    def _compute_hours(self):
        """Return a dict of [id][fields]"""
        self.ensure_one()
        result = {}
        aal_obj = self.env['account.analytic.line']
        for block in self:
            result[block.id] = {'amount_hours_block': 0.0,
                                'amount_hours_block_done': 0.0}
            # Compute hours bought
            for line in block.invoice_id.invoice_line:
                hours_bought = 0.0
                if line.product_id and line.product_id.is_in_hours_block:
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
            res_line_ids = []
            if block.invoice_id:
                self.env.cr.execute("SELECT al.id "
                                    "FROM account_analytic_line AS al, "
                                    "     account_analytic_journal AS aj "
                                    "WHERE aj.id = al.journal_id "
                                    "AND aj.type = 'general' "
                                    "AND al.invoice_id = %s",
                                    (block.invoice_id.id,))
                res_line_ids = self.env.cr.fetchall()
            line_ids = [l[0] for l in res_line_ids] if res_line_ids else []
            for line in aal_obj.browse(line_ids):
                factor = 1.0
                if line.product_uom_id and line.product_uom_id.factor != 0.0:
                    factor = line.product_uom_id.factor
                factor_invoicing = 1.0
                if line.to_invoice and line.to_invoice.factor != 0.0:
                    factor_invoicing = 1.0 - line.to_invoice.factor / 100
                hours_used += ((line.unit_amount / factor) * factor_invoicing)
            result[block.id]['amount_hours_block_done'] = hours_used
        return result

    @api.multi
    def _compute_amount(self):
        self.ensure_one()
        result = {}
        aal_obj = self.env['account.analytic.line']
        pricelist_obj = self.env['product.pricelist']
        for block in self:
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
            # Get ids of analytic line generated from timesheet associated
            # to current block
            res_line_ids = []
            if block.invoice_id:
                self.env.cr.execute("SELECT al.id "
                                    "FROM account_analytic_line AS al,"
                                    " account_analytic_journal AS aj"
                                    " WHERE aj.id = al.journal_id"
                                    "  AND aj.type='general'"
                                    "  AND al.invoice_id = %s",
                                    (block.invoice_id.id,))
                res_line_ids = self.env.cr.fetchall()
            line_ids = [l[0] for l in res_line_ids] if res_line_ids else []
            total_amount = 0.0
            for line in aal_obj.browse(line_ids):
                factor_invoicing = 1.0
                if line.to_invoice and line.to_invoice.factor != 0.0:
                    factor_invoicing = 1.0 - line.to_invoice.factor / 100

                ctx = dict(self.env.context, uom=line.product_uom_id.id)
                amount = pricelist_obj.with_context(ctx).price_get(
                    [line.account_id.pricelist_id.id],
                    line.product_id.id,
                    line.unit_amount or 1.0,
                    line.account_id.partner_id.id or False
                    )[line.account_id.pricelist_id.id]
                total_amount += amount * line.unit_amount * factor_invoicing
            result[block.id]['amount_hours_block_done'] += total_amount

        return result

    @api.depends(
        'invoice_id',
        'invoice_id.invoice_line',
        'type',
        )
    def _compute(self):
        for block in self:
            result = {}
            if block.type:
                result = getattr(self, "_compute_%s" % block.type)()
            res = result.get(block.id, {})
            block.amount_hours_block = res.get('amount_hours_block', 0)
            block.amount_hours_block_done = (
                res.get('amount_hours_block_done', 0)
            )

    @api.depends('amount_hours_block_done', 'amount_hours_block')
    def _compute_delta(self):
        for rec in self:
            rec.amount_hours_block_delta = (
                self.amount_hours_block - self.amount_hours_block_done
            )

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

    @api.model
    def _type_get(self):
        return [('hours', 'Hours'),
                ('amount', 'Amount')
                ]

    amount_hours_block = fields.Float(
        string='Quantity / Amount bought',
        compute=_compute,
        store=True,
        help="Amount bought by the customer. "
        "This amount is expressed in the base Unit of Measure "
        "(factor=1.0)")
    amount_hours_block_done = fields.Float(
        string='Quantity / Amount used',
        compute=_compute,
        store=True,
        help="Amount done by the staff. "
             "This amount is expressed in the base Unit of Measure "
             "(factor=1.0)")
    amount_hours_block_delta = fields.Float(
        string='Difference',
        compute=_compute,
        store=True,
        help="Difference between bought and used. "
             "This amount is expressed in the base Unit of Measure "
             "(factor=1.0)")
    last_action_date = fields.Date(
        string='Last action date',
        compute=_get_last_action,
        help="Date of the last analytic line linked to the invoice "
             "related to this block hours.")
    close_date = fields.Date(string='Closed Date')
    invoice_id = fields.Many2one('account.invoice', string='Invoice',
                                 required=True, ondelete='cascade')
    type = fields.Selection(
        '_type_get',
        string='Type of Block',
        required=True,
        help="The block is based on the quantity of hours "
             "or on the amount.")
    date_invoice = fields.Date(string='Invoice Date',
                               related="invoice_id.date_invoice",
                               readonly=True,
                               store=True,
                               )
    user_id = fields.Many2one('res.users', string='Salesman',
                              store=True,
                              related="invoice_id.user_id", readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 store=True,
                                 related="invoice_id.partner_id",
                                 readonly=True,)
    name = fields.Char(string='Description',
                       related="invoice_id.name",
                       store=True,
                       readonly=True,)
    number = fields.Char(string='Number',
                         related="invoice_id.number",
                         store=True,
                         readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal',
                                 related="invoice_id.journal_id",
                                 store=True,
                                 readonly=True)
    period_id = fields.Many2one('account.period', string='Period',
                                related="invoice_id.period_id",
                                store=True,
                                readonly=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 related="invoice_id.company_id",
                                 store=True,
                                 readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related="invoice_id.currency_id",
                                  store=True,
                                  readonly=True)
    residual = fields.Float(string='Residual',
                            related="invoice_id.residual",
                            store=True,
                            readonly=True)
    amount_total = fields.Float(string='Total',
                                related="invoice_id.amount_total",
                                store=True,
                                readonly=True)
    department_id = fields.Many2one('hr.department', string='Department',
                                    related="invoice_id.department_id",
                                    store=True,
                                    readonly=True)

    @api.model
    def _state_get(self):
        return [
            ('draft', 'Draft'),
            ('proforma', 'Pro-forma'),
            ('proforma2', 'Pro-forma'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
            ]

    state = fields.Selection('_state_get', string='State',
                             related="invoice_id.state",
                             store=True,
                             readonly=True)


############################################################################
# Add hours blocks on invoice
############################################################################
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    account_hours_block_ids = fields.One2many('account.hours.block',
                                              'invoice_id',
                                              string='Hours Block')
