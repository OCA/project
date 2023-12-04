# Copyright 2022-2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    def _prepare_stock_move_values(self, task, quantity):
        self.ensure_one()
        values = {
            "name": self.product_id.display_name,
            "product_id": self.product_id.id,
            "product_uom_qty": self.quantity * quantity,
            "product_uom": self.product_id.uom_id.id,
            "state": "draft",
            "raw_material_task_id": task.id,
        }
        # According to default values set from stock_move field in task form
        stock_move_model = self.env["stock.move"].with_context(
            default_raw_material_task_id=task.id
        )
        values.update(
            stock_move_model.default_get(
                ["group_id", "location_id", "location_dest_id", "picking_type_id"]
            )
        )
        return values
