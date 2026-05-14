# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProjectTaskProduct(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
            }
        )

    def test_product_task_count(self):
        """Task count on product.product must count only tasks linked to it."""

        self.assertEqual(self.product.task_count, 0)
        self.env["project.task"].create(
            {
                "name": "Task 1",
                "product_id": self.product.id,
                "project_id": self.project.id,
            }
        )

        self.env["project.task"].create(
            {
                "name": "Task 2",
                "product_id": self.product.id,
                "project_id": self.project.id,
            }
        )
        self.product._compute_task_count()
        self.assertEqual(self.product.task_count, 2)

    def test_product_action_view_tasks(self):
        """Check action domain + context for product.product."""
        action = self.product.action_view_tasks()

        self.assertEqual(action["domain"], [("product_id", "in", [self.product.id])])
        self.assertEqual(action["context"]["default_product_id"], self.product.id)

    def test_template_task_count(self):
        """Task count on product.template must sum all variant tasks."""
        template = self.product.product_tmpl_id
        variant2 = self.env["product.product"].create(
            {"name": "Test Product 2", "product_tmpl_id": template.id}
        )

        self.assertEqual(template.task_count, 0)

        self.env["project.task"].create(
            {
                "name": "Task 1",
                "product_id": self.product.id,
                "project_id": self.project.id,
            }
        )

        self.env["project.task"].create(
            {"name": "Task 2", "product_id": variant2.id, "project_id": self.project.id}
        )

        template._compute_task_count()
        self.assertEqual(template.task_count, 2)

    def test_template_action_view_tasks(self):
        """Check action domain for product.template."""
        template = self.product.product_tmpl_id

        action = template.action_view_tasks()

        self.assertEqual(action["domain"], [("product_id", "in", [self.product.id])])
