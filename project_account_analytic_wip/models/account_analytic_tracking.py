# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AnalyticTrackingItem(models.Model):
    _inherit = "account.analytic.tracking.item"

    sale_order_line_id = fields.Many2one(
        "sale.order.line", string="Order Line", ondelete="set null"
    )

    @api.depends("sale_order_line_id")
    def _compute_name(self):
        super()._compute_name()
        for tracking in self.filtered("sale_order_line_id"):
            tracking.name = tracking.sale_order_line_id.display_name
