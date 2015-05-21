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


class SaleToProject(models.TransientModel):
    _name = 'sale.to.project'
    _description = 'Create Contract from Sales Order'

    create_contract_method = fields.Selection(
        selection=[('all', 'Create Contract from all the lines'),
                   ('lines', 'Create Contract from a selection of lines')],
        string='Method',
        default='all',
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
    def open_contract(self, contract):
        action_xmlid = ('account_analytic_analysis.'
                        'action_account_analytic_overdue_all')
        action = self.env.ref(action_xmlid).read()[0]
        action['context'] = {}
        action['views'] = [(False, 'form')]
        action['res_id'] = contract.id
        return action

    @api.multi
    def create_contract(self):
        self.ensure_one()
        sale_ids = self.env.context.get('active_ids')
        sale = self.env['sale.order'].browse(sale_ids)
        sale.ensure_one()
        contract = sale.create_contract()

        if self.env.context.get('open_contract'):
            return self.open_contract(contract)
        return {'type': 'ir.actions.act_window_close'}
