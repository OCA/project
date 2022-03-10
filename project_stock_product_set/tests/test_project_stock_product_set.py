# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.project_stock.tests.common import TestProjectStockBase


class TestProjectStockProductSet(TestProjectStockBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.task = cls._create_task(cls, [])
        cls.product_set = cls.env["product.set"].create(
            {
                "name": "Test product set",
                "set_line_ids": [
                    (0, 0, {"product_id": cls.product_a.id, "quantity": 2}),
                    (0, 0, {"product_id": cls.product_b.id, "quantity": 1}),
                ],
            }
        )

    def test_wizard_product_set_add(self):
        self.assertFalse(self.task.move_ids)
        wizard_form = Form(
            self.env["product.set.add.from.task"].with_context(
                default_task_id=self.task.id
            )
        )
        wizard_form.product_set_id = self.product_set
        wizard = wizard_form.save()
        wizard.add_set()
        self.assertEqual(len(self.task.move_ids), 2)
        self.assertIn(self.product_a, self.task.move_ids.mapped("product_id"))
        self.assertIn(self.product_b, self.task.move_ids.mapped("product_id"))
        self.assertEqual(sum(self.task.move_ids.mapped("product_uom_qty")), 3)
