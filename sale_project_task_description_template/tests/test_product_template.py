# Copyright 2025 NICO SOLUTIONS - ENGINEERING & IT
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo.tests.common import TransactionCase


class TestProductTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.task_template = cls.env["project.task.description.template"].create(
            {
                "name": "Test Task Template",
                "description": "Template Description",
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "task_description_template_id": cls.task_template.id,
                "include_sale_line_info_in_task": True,
            }
        )

    def test_template_assignment(self):
        self.assertEqual(
            self.product.task_description_template_id,
            self.task_template,
            "Template should be saved correctly in the product.",
        )

    def test_flag_include_sale_line_info(self):
        self.product.include_sale_line_info_in_task = False
        self.assertFalse(
            self.product.include_sale_line_info_in_task,
            "Flag should be False after change.",
        )
