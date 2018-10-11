# Copyright 2018 José Luis Sandoval Alaguna - Rotafilo
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api


class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.multi
    def _compute_num_sale_orders(self):
        order = self.env['sale.order']
        for analytic_account in self:
            domain = ('analytic_account_id', '=', analytic_account.id)
            analytic_account.num_sale_orders = order.search_count([domain])

    num_sale_orders = fields.Integer(
        compute="_compute_num_sale_orders",
        string="Number of sale orders"
    )
