# Copyright 2016 Tecnativa - Vicent Cubells
# Copyright 2018 - Brain-tec AG - Carlos Jesus Cebrian
# Copyright 2026 Mario Castillo López <@mcastillol14>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo.exceptions import ValidationError

from .common import TestProjectCases


class ProjectTaskMaterial(TestProjectCases):
    def test_manager_add_task_material_wrong(self):
        """Adding a material with quantity 0 or negative must fail."""
        try:
            self.action.write(
                {
                    "material_ids": [
                        (0, 0, {"product_id": self.product.id, "quantity": 0.0})
                    ]
                }
            )
        except ValidationError as err:
            self.assertEqual(
                str(err.args[0]),
                "Quantity of material consumed must be greater than 0.",
            )

        try:
            self.action.write(
                {
                    "material_ids": [
                        (0, 0, {"product_id": self.product.id, "quantity": -10.0})
                    ]
                }
            )
        except ValidationError as err:
            self.assertEqual(
                str(err.args[0]),
                "Quantity of material consumed must be greater than 0.",
            )

    def test_manager_add_task_material_right(self):
        """Adding a material with a valid quantity must succeed."""
        self.action.write(
            {"material_ids": [(0, 0, {"product_id": self.product.id, "quantity": 4.0})]}
        )
        self.assertEqual(len(self.task.material_ids.ids), 1)
