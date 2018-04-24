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

from openerp import models, fields, api, exceptions, _


class SaleToProject(models.TransientModel):
    _name = 'sale.to.project'
    _description = 'Create Contract from Sales Order'

    create_contract_method = fields.Selection(
        selection=[('all', 'Create Contract from all the lines'),
                   ('lines', 'Create Contract from a selection of lines')],
        string='Method',
        default='all',
        required=True,
    )

    @api.multi
    def open_lines(self):
        sale_ids = self.env.context.get('active_ids')
        action_xmlid = 'sale.action_order_line_tree2'
        action = self.env.ref(action_xmlid).read()[0]
        action['context'] = {
            'search_default_uninvoiced': 1,
            'search_default_order_id': sale_ids[0] if sale_ids else False,
        }
        return action

    @api.multi
    def button_create_contract(self):
        self.ensure_one()
        sale_ids = self.env.context.get('active_ids')
        sale = self.env['sale.order'].browse(sale_ids)
        sale.ensure_one()
        contract = self.create_contract(sale)

        if self.env.context.get('open_contract'):
            return sale._open_contracts(contracts=contract)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def _prepare_contract_line(self, line):
        return {
            'product_id': line.product_id.id,
            'name': line.name,
            'quantity': line.product_uom_qty,
            'uom_id': line.product_uom.id,
            'price_unit': line.price_unit,
            'sale_line_id': line.id,
        }

    @api.multi
    def _prepare_contract(self, sale, lines):
        dt_from_str = fields.Datetime.from_string
        d_to_str = fields.Date.to_string
        values = {'name': '%s - %s' % (sale.partner_id.name, sale.name),
                  'partner_id': sale.partner_id.id,
                  'manager_id': sale.user_id.id,
                  'code': sale.name,
                  'company_id': sale.company_id.id,
                  'date_start': d_to_str(dt_from_str(sale.date_order)),
                  'recurring_invoices': True,
                  'type': 'contract',
                  'sale_id': sale.id,
                  }
        values['recurring_invoice_line_ids'] = [
            (0, 0, self._prepare_contract_line(line))
            for line in lines
        ]
        return values

    @api.multi
    def create_contract(self, sale, lines=None):
        sale.ensure_one()
        if lines and any(line.order_id != sale for line in lines):
            raise exceptions.Warning(
                _('Cannot create a contract for lines of different orders')
            )
        elif not lines:
            lines = sale.order_line
        lines = lines.filtered(lambda line: (not line.in_contract and
                                             not line.invoiced))
        if not lines:
            raise exceptions.Warning(
                _('There are no lines to create a contract.')
            )
        contract_model = self.env['account.analytic.account']
        contract = contract_model.create(self._prepare_contract(sale, lines))
        if all(line.state == 'cancel' or line.invoiced or line.in_contract
                for line in sale.order_line):
            sale.signal_workflow('all_lines')
        return contract
