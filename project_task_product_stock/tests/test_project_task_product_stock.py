# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProjectTaskProductStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
            }
        )

    def test_lot_task_count(self):
        """Task count on stock.lot must count only tasks with correct product + lot."""
        product = self.product
        lot = self.env["stock.lot"].create({"name": "Lot A", "product_id": product.id})

        # Task with lot -> should count
        self.env["project.task"].create(
            {"name": "Task 1", "product_id": product.id, "lot_id": lot.id}
        )

        # Task without lot -> must not count
        self.env["project.task"].create({"name": "Task 2", "product_id": product.id})

        lot._compute_task_count()
        self.assertEqual(lot.task_count, 1)

    def test_lot_action_view_tasks(self):
        """Check action domain + context for stock.lot."""
        product = self.product
        lot = self.env["stock.lot"].create({"name": "Lot A", "product_id": product.id})

        action = lot.action_view_tasks()

        self.assertEqual(
            action["domain"], [("product_id", "=", product.id), ("lot_id", "=", lot.id)]
        )
        self.assertEqual(action["context"]["default_product_id"], product.id)
        self.assertEqual(action["context"]["default_lot_id"], lot.id)
