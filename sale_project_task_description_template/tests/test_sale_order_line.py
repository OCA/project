# Copyright 2025 NICO SOLUTIONS - ENGINEERING & IT
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo.tests.common import TransactionCase


class TestSaleOrderLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.task_template = cls.env["project.task.description.template"].create(
            {
                "name": "Test Template",
                "description": "Template Description",
            }
        )
        cls.empty_template = cls.env["project.task.description.template"].create(
            {
                "name": "Empty Template",
                "description": "",
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "task_description_template_id": cls.task_template.id,
                "include_sale_line_info_in_task": True,
            }
        )
        cls.partner = cls.env["res.partner"].search([], limit=1)
        cls.sale_order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "billing_type": "not_billable",
                "allow_timesheets": True,
            }
        )

    def _prepare_task_values(self, include_sale_line_info=False, template=None, qty=1):
        self.product.include_sale_line_info_in_task = include_sale_line_info
        self.product.task_description_template_id = template or False
        sale_line = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "product_id": self.product.product_variant_id.id,
                "product_uom_qty": qty,
            }
        )
        return sale_line._timesheet_create_task_prepare_values(project=self.project)

    def test_task_values_without_template(self):
        values = self._prepare_task_values(
            include_sale_line_info=False, template=None, qty=1
        )
        self.assertNotIn("description_template_id", values)
        self.assertIn("description", values)
        self.assertEqual(values["description"], "")

    def test_task_values_with_template_only(self):
        values = self._prepare_task_values(
            include_sale_line_info=False, template=self.task_template, qty=2
        )
        self.assertIn("description_template_id", values)
        self.assertEqual(values["description_template_id"], self.task_template.id)
        self.assertEqual(values["description"], self.task_template.description)

    def test_task_values_with_template_and_sale_info(self):
        values = self._prepare_task_values(
            include_sale_line_info=True, template=self.task_template, qty=3
        )
        expected_prefix = f"{self.product.name} - Qty: 3"
        self.assertIn("description_template_id", values)
        self.assertTrue(values["description"].startswith(expected_prefix))
        self.assertIn(self.task_template.description, values["description"])

    def test_task_values_with_empty_template_only(self):
        values = self._prepare_task_values(
            include_sale_line_info=False, template=self.empty_template, qty=5
        )
        self.assertIn("description", values)
        self.assertEqual(values["description"], "")
        self.assertIn("description_template_id", values)

    def test_task_values_with_empty_template_and_sale_info(self):
        values = self._prepare_task_values(
            include_sale_line_info=True, template=self.empty_template, qty=4
        )
        expected_prefix = f"{self.product.name} - Qty: 4.0"
        self.assertIn("description", values)
        self.assertEqual(values["description"], expected_prefix)
        self.assertIn("description_template_id", values)
