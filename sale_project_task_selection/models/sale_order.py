# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    has_project_service_tracking_lines = fields.Boolean(
        compute="_compute_has_project_service_tracking_lines"
    )

    @api.depends("order_line.is_project_service_tracking_line")
    def _compute_has_project_service_tracking_lines(self):
        """Compute if the order has any line with project service tracking."""
        for order in self:
            order.has_project_service_tracking_lines = any(
                line.is_project_service_tracking_line for line in order.order_line
            )
