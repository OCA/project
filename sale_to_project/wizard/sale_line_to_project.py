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

from openerp import models, api


class SaleLineToProject(models.TransientModel):
    _name = 'sale.line.to.project'
    _description = 'Create Contract from Sales Order Lines'

    @api.multi
    def button_create_contract(self):
        self.ensure_one()
        sale_line_ids = self.env.context.get('active_ids')
        sale_lines = self.env['sale.order.line'].browse(sale_line_ids)
        sale = sale_lines[0].order_id
        contract = self.create_contract(sale, sale_lines)

        if self.env.context.get('open_contract'):
            return sale._open_contracts(contracts=contract)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def _prepare_sale_to_project_wizard(self, sale, lines):
        return {}

    @api.multi
    def create_contract(self, sale, lines):
        sale_to_project_model = self.env['sale.to.project']
        sale_to_project = sale_to_project_model.create(
            self._prepare_sale_to_project_wizard(sale, lines)
        )
        return sale_to_project.create_contract(sale, lines=lines)
