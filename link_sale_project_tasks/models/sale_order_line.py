# -*- coding: utf-8 -*-
# © 2017 Le Filament (<http://www.le-filament.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _compute_analytic(self, domain=None):
        if not domain and self.ids:
            # To filter on analyic lines linked to an expense
            expense_type_id = self.env.ref(
                'account.data_account_type_expenses',
                raise_if_not_found=False
                )
            expense_type_id = expense_type_id and expense_type_id.id
            prod_list = self.env['product.template'].search(
                [('track_service', 'in', ['task', 'timesheet'])]
                )
            domain = [
                ('product_id', 'in', prod_list.ids),
                ('so_line', 'in', self.ids),
                '|', ('amount', '<=', 0.0), ('project_id', '!=', False)
                ]
        return super(SaleOrderLine, self)._compute_analytic(
            domain=domain)
