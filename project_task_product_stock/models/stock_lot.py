# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    task_count = fields.Integer(compute="_compute_task_count")

    def _compute_task_count(self):
        task_data = self.env["project.task"]._read_group(
            [
                ("product_id", "in", self.mapped("product_id").ids),
                ("lot_id", "in", self.ids),
            ],
            groupby=["product_id", "lot_id"],
            aggregates=["__count"],
        )

        mapped = {(product.id, lot.id): count for product, lot, count in task_data}

        for lot in self:
            lot.task_count = mapped.get(
                (lot.product_id.id, lot.id),
                0,
            )

    def action_view_tasks(self):
        action = self.env["ir.actions.actions"]._for_xml_id("project.action_view_task")
        action.update(
            {
                "domain": [
                    ("product_id", "=", self.product_id.id),
                    ("lot_id", "=", self.id),
                ],
                "context": {
                    "default_product_id": self.product_id.id,
                    "default_lot_id": self.id,
                },
            }
        )
        return action
