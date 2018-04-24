# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
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
#

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_ids = fields.One2many(
        comodel_name='account.analytic.account',
        inverse_name='sale_id',
        string='Contracts',
    )

    @api.multi
    def _open_contracts(self, contracts=None):
        self.ensure_one()
        action_xmlid = ('account_analytic_analysis.'
                        'action_account_analytic_overdue_all')
        action = self.env.ref(action_xmlid).read()[0]
        action['context'] = {}
        if contracts is None:
            contracts = self.contract_ids

        if len(contracts) == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = contracts.id
        else:
            action['domain'] = [('id', 'in', contracts.ids)]
        return action

    @api.multi
    def open_contracts(self):
        """ Called from a button. Open the related contracts

        We cannot have a keyword argument on methods called from a button.
        That's why there are 2 methods.
        """
        return self._open_contracts()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    recurring_invoice_line_ids = fields.One2many(
        comodel_name='account.analytic.invoice.line',
        inverse_name='sale_line_id',
        string='Recurring Invoice Lines',
    )
    in_contract = fields.Boolean(compute='_compute_in_contract',
                                 string='In a Contract')
    invoiced = fields.Boolean(compute='_compute_invoiced', store=True)

    @api.one
    @api.depends('order_id.state',
                 'invoice_lines',
                 'invoice_lines.invoice_id.state',
                 'recurring_invoice_line_ids',
                 'recurring_invoice_line_ids.analytic_account_id.state',
                 'in_contract')
    def _compute_invoiced(self):
        invoiced = self._fnct_line_invoiced(['invoiced'], []).get(self.id)
        self.invoiced = invoiced or self.in_contract

    @api.one
    @api.depends('recurring_invoice_line_ids',
                 'recurring_invoice_line_ids.analytic_account_id.state')
    def _compute_in_contract(self):
        self.in_contract = any(
            line.analytic_account_id.state != 'cancelled'
            for line in self.recurring_invoice_line_ids
        )
