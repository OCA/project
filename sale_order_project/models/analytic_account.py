# © 2018 José Luis Sandoval Alaguna - Rotafilo
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields


class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    def _compute_num_productions(self):
        for analytic_account in self:
            analytic_account.num_sale_orders = self.env['sale.order'].search_count([
                ('analytic_account_id','=', analytic_account.id)
            ])

    num_sale_orders = fields.Integer(compute="_compute_num_sale_orders", string="Number of sale orders")
