# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    def _prepare_stock_move_values(self, task, quantity):
        self.ensure_one()
        values = {
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
        values.update(self.env["stock.move"].play_onchanges(values, values.keys()))
        # We need to remove product_qty to prevent error
        # The requested operation cannot be processed because of a programming error
        # setting the `product_qty` field instead of the `product_uom_qty`.
        del values["product_qty"]
        return values
