# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests.common import TransactionCase


class TestCopyTasks(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.analytic_account_sale = cls.env["account.analytic.account"].create(
            {"name": "Project for selling timesheet - AA", "code": "AA-2030"}
        )

        # Create projects
        cls.project_template = cls.env["project.project"].create(
            {
                "name": "Project template",
            }
        )
        cls.project_template_state = cls.env["project.task.type"].create(
            {
                "name": "Only stage in project template",
                "sequence": 1,
                "project_ids": [(4, cls.project_template.id)],
            }
        )
        cls.project_template_tasks = cls.env["project.task"].create(
            [
                {
                    "name": "Task template 1",
                    "stage_id": cls.project_template_state.id,
                    "project_id": cls.project_template.id,
                },
                {
                    "name": "Task template 2",
                    "stage_id": cls.project_template_state.id,
                    "project_id": cls.project_template.id,
                },
                {
                    "name": "Task template 3",
                    "stage_id": cls.project_template_state.id,
                    "project_id": cls.project_template.id,
                },
                {
                    "name": "Task template 4",
                    "stage_id": cls.project_template_state.id,
                    "project_id": cls.project_template.id,
                },
            ]
        )

        # Create service products
        uom_hour = cls.env.ref("uom.product_uom_hour")

        cls.product_order_service1 = cls.env["product.product"].create(
            {
                "name": "Service Ordered, create task in project's order",
                "standard_price": 30,
                "list_price": 90,
                "type": "service",
                "invoice_policy": "order",
                "uom_id": uom_hour.id,
                "uom_po_id": uom_hour.id,
                "default_code": "SERV-COPY-TASK",
                "service_tracking": "copy_tasks_in_project",
                "project_id": False,
                "project_template_id": cls.project_template.id,
            }
        )

    def test_sale_order_with_copy_tasks(self):
        so_model = self.env["sale.order"].with_context(tracking_disable=True)
        sol_model = self.env["sale.order.line"].with_context(tracking_disable=True)

        partner = self.env["res.partner"].create({"name": "Test Partner"})
        sale_order_1 = so_model.create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
            }
        )
        so_1_line_1_copy_task = sol_model.create(
            {
                "name": self.product_order_service1.name,
                "product_id": self.product_order_service1.id,
                "product_uom_qty": 1,
                "product_uom": self.product_order_service1.uom_id.id,
                "price_unit": self.product_order_service1.list_price,
                "order_id": sale_order_1.id,
            }
        )
        sale_order_1.action_confirm()
        # Project must be created and all tasks inherited
        self.assertEqual(
            sale_order_1.name,
            sale_order_1.project_id.name,
            "SO1: Project name different than sale project",
        )
        self.assertEqual(
            so_1_line_1_copy_task.project_id,
            sale_order_1.project_id,
            "SO1L1: Sale project different from line",
        )
        self.assertTrue(
            sale_order_1.project_id.analytic_account_id,
            "SO1: Analytic account not created",
        )
        self.assertEqual(
            sale_order_1.project_id.analytic_account_id,
            sale_order_1.analytic_account_id,
            "SO1: Different analytic accounts",
        )
        self.assertEqual(
            len(sale_order_1.project_id.task_ids),
            len(self.project_template_tasks),
            "SO1L1: Different number of tasks inherited",
        )

        # Cancel and draft sale in order to add more lines
        so_1_line_2_copy_task = sol_model.create(
            {
                "name": self.product_order_service1.name,
                "product_id": self.product_order_service1.id,
                "product_uom_qty": 1,
                "product_uom": self.product_order_service1.uom_id.id,
                "price_unit": self.product_order_service1.list_price,
                "order_id": sale_order_1.id,
            }
        )
        # New tasks must be added to the existing project
        self.assertEqual(
            so_1_line_2_copy_task.project_id,
            sale_order_1.project_id,
            "SO1L2: New added Line project different from line",
        )
        self.assertEqual(
            len(sale_order_1.project_id.task_ids),
            len(self.project_template_tasks) * 2,
            "SO1L2: Different number of tasks inherited when adding another line",
        )

        # New sale order for the same project
        sale_order_2 = so_model.create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
                "project_id": sale_order_1.project_id.id,  # Specify project
            }
        )
        sale_order_2._onchange_project_id()
        so_2_line_1_copy_tasks = sol_model.create(
            {
                "product_id": self.product_order_service1.id,
                "product_uom_qty": 1,
                "product_uom": self.product_order_service1.uom_id.id,
                "price_unit": self.product_order_service1.list_price,
                "order_id": sale_order_2.id,
            }
        )
        sale_order_2.action_confirm()
        self.assertNotEqual(
            sale_order_2.name,
            sale_order_2.project_id.name,
            "SO2: Project has been renamed",
        )
        self.assertEqual(
            so_2_line_1_copy_tasks.project_id,
            sale_order_2.project_id,
            "SO2L1: Line project different from line",
        )
        self.assertEqual(
            len(sale_order_2.project_id.task_ids),
            len(self.project_template_tasks) * 3,
            "SO2L1: Different number of tasks inherited",
        )
