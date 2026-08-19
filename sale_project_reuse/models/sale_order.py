# Copyright 2026 glueckkanja AG
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _apply_reuse_project(self):
        """Set the customer's project on the order, without overwriting."""
        self.ensure_one()
        if self.project_id or not self.order_line._get_reuse_project_lines():
            return
        self.project_id = self.partner_id.commercial_partner_id.reuse_project_id

    def _remember_reuse_project(self):
        """Store the project of the order as the customer's project to reuse."""
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id
        if (
            partner.reuse_project_id
            or not self.project_id
            or not self.order_line._get_reuse_project_lines()
        ):
            return
        # Salesmen may not have write access on the customer
        partner.sudo().reuse_project_id = self.project_id

    @api.onchange("order_line", "partner_id")
    def _onchange_order_line_reuse_project(self):
        self._apply_reuse_project()

    def _action_confirm(self):
        """Reuse the customer's project, or remember the one of this order."""
        for order in self:
            order._apply_reuse_project()
        res = super()._action_confirm()
        for order in self:
            order._remember_reuse_project()
        return res
