# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    def prepare_stock_move_values(self, task, quantity):
        self.ensure_one()
        return {
            "product_id": self.product_id.id,
            "product_uom_qty": self.quantity * quantity,
            "product_uom": self.product_id.uom_id.id,
            # According to default values set from stock_move field in task form
            "location_id": (task.location_id.id or task.project_id.location_id.id),
            "location_dest_id": (
                task.location_dest_id.id or task.project_id.location_dest_id.id
            ),
            "state": "draft",
            "raw_material_task_id": task.id,
            "picking_type_id": task.picking_type_id.id,
        }
