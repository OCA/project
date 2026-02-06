# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo.tests import tagged

from odoo.addons.project_task_material.tests.test_create_material_lines import (
    ProjectTaskMaterial,
)


@tagged("post_install", "-at_install")
class ProjectTaskMaterialCost(ProjectTaskMaterial):
    def test_01_add_task_material_cost(self):
        """Add product with cost"""
        self.action.write(
            {"material_ids": [(0, 0, {"product_id": self.product.id, "quantity": 4.0})]}
        )
        self.assertEqual(len(self.task.material_ids.ids), 1)
        self.assertEqual(
            self.task.material_ids.cost,
            self.task.material_ids.product_id.standard_price,
        )
