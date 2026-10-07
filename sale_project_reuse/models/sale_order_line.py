# Copyright 2026 glueckkanja AG
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_reuse_project_lines(self):
        """Lines whose product asks to reuse the project of the customer."""
        return self.filtered("product_id.reuse_project")

    def _timesheet_service_generation(self):
        """Reuse the project of the order instead of generating a new one.

        Odoo only skips the generation of a project when the line already has
        one, so the project of the order is assigned upfront.
        """
        lines_to_reuse = self._get_reuse_project_lines().filtered(
            lambda sol: sol.is_service
            and not sol.project_id
            and sol.order_id.project_id
        )
        for line in lines_to_reuse:
            line.project_id = line.order_id.project_id
        return super()._timesheet_service_generation()
