# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    lot_id = fields.Many2one(
        "stock.lot",
        string="Lot/Serial Number",
        tracking=True,
        check_company=True,
    )

    product_tracking = fields.Selection(
        related="product_id.tracking", string="Product Tracking", readonly=True
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """Reset Lot if Product changes"""
        if self.lot_id and self.lot_id.product_id != self.product_id:
            self.lot_id = False

    @api.onchange("lot_id")
    def _onchange_lot_id(self):
        """Set Product based on Lot selection"""
        if self.lot_id:
            self.product_id = self.lot_id.product_id
