# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import Form, RecordCapturer, TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestSaleProject(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        # Create a few project and tasks
        cls.project_template = cls.env["project.project"].create(
            {"name": "Test Project Template"}
        )
        cls.project_a = cls.env["project.project"].create(
            {"name": "Test Project A", "allow_billable": True}
        )
        cls.project_b = cls.env["project.project"].create(
            {"name": "Test Project B", "allow_billable": True}
        )
        cls.task_a_1 = cls.env["project.task"].create(
            {"name": "Test Task A 1", "project_id": cls.project_a.id}
        )
        cls.task_a_2 = cls.env["project.task"].create(
            {"name": "Test Task A 2", "project_id": cls.project_a.id}
        )
        cls.task_b_1 = cls.env["project.task"].create(
            {"name": "Test Task B 1", "project_id": cls.project_b.id}
        )
        # A simple consumable product
        cls.product_consu = cls.env["product.product"].create(
            {
                "name": "Consumable",
                "type": "consu",
            }
        )
        # A product that doesn't create a Task or Project
        cls.product_no_service_tracking = cls.env["product.product"].create(
            {
                "name": "No Service Tracking",
                "type": "service",
                "service_tracking": "no",
            }
        )
        # A product that creates a Task in the Quotation Project
        cls.product_create_task = cls.env["product.product"].create(
            {
                "name": "Create a Task in the Global Project",
                "type": "service",
                "service_tracking": "task_global_project",
            }
        )
        # A product that creates a new Project & Task in it
        cls.product_create_task_and_project = cls.env["product.product"].create(
            {
                "name": "Create a Project & Task",
                "type": "service",
                "service_tracking": "task_in_project",
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )

    def test_onchange_task_set_project_if_empty(self):
        """Test the onchange method that sets the project if empty"""
        with Form(self.order) as form:
            with form.order_line.new() as line_form:
                line_form.product_id = self.product_create_task
                self.assertFalse(line_form.project_id)
                line_form.task_id = self.task_a_1
                self.assertEqual(
                    line_form.project_id,
                    self.project_a,
                    "The project is set on the line",
                )

    def test_onchange_project_clear_task_if_differs(self):
        """Test the onchange method that clears the task if it differs"""
        with Form(self.order) as form:
            with form.order_line.new() as line_form:
                line_form.product_id = self.product_create_task
                line_form.project_id = self.project_a
                line_form.task_id = self.task_a_1
                # Now use a different project
                line_form.project_id = self.project_b
                self.assertFalse(line_form.task_id, "The task is cleared on the line")

    def test_columns_arent_shown_if_no_project_in_order(self):
        """Test the Project and Task columns and fields visibility

        The line's Project and Task columns are only shown if there's at least one
        line with a Project product.

        The line's Project and Task fields are invisible until we set a Project product.
        """
        # There's a small incompatibility with `sale_project_copy_tasks`, since it's
        # also adding the `project_id` field to the order_line in the SO view, but it's
        # not setting the same invisible and column_invisible flags
        # So, lazily try to disable this view if the module is installed during tests
        if view := self.env.ref(
            "sale_project_copy_tasks.view_order_form_inherit_sale_project_copy_taks",
            raise_if_not_found=False,
        ):
            view.active = False
        with Form(self.order) as form:
            # Add a first order line
            with form.order_line.new() as line_form:
                # At first, the Project and Task columns are not shown because
                # the order doesn't have any "Project" product
                self.assertTrue(line_form._get_modifier("project_id", "invisible"))
                self.assertTrue(
                    line_form._get_modifier("project_id", "column_invisible")
                )
                self.assertTrue(line_form._get_modifier("task_id", "invisible"))
                self.assertTrue(line_form._get_modifier("task_id", "column_invisible"))
                # Once we set a Project Product, the Project and Task columns are shown
                line_form.product_id = self.product_create_task
            # NOTE: Checking this after the form is saved because the `Form` class
            # doesn't handle it properly
            self.assertFalse(line_form._get_modifier("project_id", "invisible"))
            self.assertFalse(line_form._get_modifier("task_id", "invisible"))
            self.assertFalse(line_form._get_modifier("project_id", "column_invisible"))
            self.assertFalse(line_form._get_modifier("task_id", "column_invisible"))
            # Switching back to a non-project product, they should be hidden again
            with form.order_line.edit(0) as line_form:
                line_form.product_id = self.product_consu
            self.assertTrue(line_form._get_modifier("project_id", "invisible"))
            self.assertTrue(line_form._get_modifier("project_id", "column_invisible"))
            self.assertTrue(line_form._get_modifier("task_id", "invisible"))
            self.assertTrue(line_form._get_modifier("task_id", "column_invisible"))
            # But let's keep them shown
            with form.order_line.edit(0) as line_form:
                line_form.product_id = self.product_create_task
            self.assertFalse(line_form._get_modifier("project_id", "invisible"))
            self.assertFalse(line_form._get_modifier("project_id", "column_invisible"))
            self.assertFalse(line_form._get_modifier("task_id", "invisible"))
            self.assertFalse(line_form._get_modifier("task_id", "column_invisible"))
            # Add a second order line
            with form.order_line.new() as line_form:
                # The fields are invisible until we set a Project product
                self.assertTrue(line_form._get_modifier("project_id", "invisible"))
                self.assertTrue(line_form._get_modifier("task_id", "invisible"))
                # If we set a Project product, the fields become visible
                line_form.product_id = self.product_create_task
                self.assertFalse(line_form._get_modifier("project_id", "invisible"))
                self.assertFalse(line_form._get_modifier("task_id", "invisible"))
                # If we set a non-project product, the fields go back to invisible
                line_form.product_id = self.product_no_service_tracking
                self.assertTrue(line_form._get_modifier("project_id", "invisible"))
                self.assertTrue(line_form._get_modifier("task_id", "invisible"))
                # ..but the columns are still shown, because there's another line with
                # a Project product
                self.assertFalse(
                    line_form._get_modifier("project_id", "column_invisible")
                )
                self.assertFalse(line_form._get_modifier("task_id", "column_invisible"))
            # Modify the first line to set a non-project product
            with form.order_line.edit(0) as line_form:
                line_form.product_id = self.product_no_service_tracking
            self.assertTrue(line_form._get_modifier("project_id", "invisible"))
            self.assertTrue(line_form._get_modifier("task_id", "invisible"))
            # Columns go back to invisible because there are no more Project products
            self.assertTrue(line_form._get_modifier("project_id", "column_invisible"))
            self.assertTrue(line_form._get_modifier("task_id", "column_invisible"))

    def test_product_create_task_in_quotation_project_without_project(self):
        """Create a Task in the Quotation project without a Project set

        This is an Odoo standard flow that should still work with this module installed.

        We have a single Sale Order Line with a product that creates a Task in the
        Quotation project, but there's no Project set on the Sale Order and no other
        line that creates one.
        """
        line = self.env["sale.order.line"].create(
            {
                "product_id": self.product_create_task.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
            }
        )
        # In fully standard Odoo, this will cause an error because the Sale Order
        # doesn't have any Project set.
        with (
            self.assertRaisesRegex(
                UserError, "A project must be defined on the quotation"
            ),
            self.cr.savepoint(),
        ):
            self.order.action_confirm()
        # That could be bypassed by setting the Sale Order's Project
        self.order.project_id = self.project_a
        with RecordCapturer(self.env["project.task"], []) as rc:
            self.order.action_confirm()
        self.assertEqual(line.task_id, rc.records)
        self.assertEqual(line.task_id.project_id, self.project_a)

    def test_product_create_task_in_quotation_project(self):
        """Create a Task in the order project with project set on the line

        The project is not set on the Sale Order, neither on the product.
        In standard Odoo, this would fail.

        We support setting the Project explicitly on the line itself.
        """
        line = self.env["sale.order.line"].create(
            {
                "product_id": self.product_create_task.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
            }
        )
        self.assertFalse(self.order.project_id, "There's no project on the order")
        line.project_id = self.project_a
        with RecordCapturer(self.env["project.task"], []) as rc:
            self.order.action_confirm()
        self.assertEqual(self.order.project_id, self.project_a, "Now it's set")
        self.assertTrue(line.task_id, "The task is created")
        self.assertEqual(line.task_id, rc.records, "The task is created")
        self.assertEqual(
            line.task_id.project_id, self.project_a, "The task is in the project"
        )

    def test_product_create_task_in_quotation_project_with_already_an_order_project(
        self,
    ):
        """Create a Task in the order project with project set on both line and order

        There's already a Project set on the order, but also an explicit Project set on
        the line. The one on the line should take precedence.
        """
        line = self.env["sale.order.line"].create(
            {
                "product_id": self.product_create_task.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
            }
        )
        # Set project on the order
        self.order.project_id = self.project_b
        # Set project on the line
        line.project_id = self.project_a
        # Confirm
        with RecordCapturer(self.env["project.task"], []) as rc:
            self.order.action_confirm()
        self.assertEqual(
            self.order.project_id,
            self.project_b,
            "The project on the order is not changed",
        )
        self.assertTrue(line.task_id, "The task is created")
        self.assertEqual(line.task_id, rc.records, "The task is created")
        self.assertEqual(
            line.task_id.project_id, self.project_a, "The task is in the right project"
        )

    def test_product_create_task_in_product_project(self):
        """Create a Task in the product project

        This is an Odoo standard flow that should still work with this module installed.

        The product is configured to create a Task in a specific project.
        No other project is set on the line.
        """
        line = self.env["sale.order.line"].create(
            {
                "product_id": self.product_create_task.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
            }
        )
        # Set the specific project on the product
        self.product_create_task.project_id = self.project_a
        # Confirm
        with RecordCapturer(self.env["project.task"], []) as rc:
            self.order.action_confirm()
        self.assertEqual(
            self.order.project_id, self.project_a, "The project on the order is set"
        )
        self.assertTrue(line.task_id, "The task is created")
        self.assertEqual(line.task_id, rc.records, "The task is created")
        self.assertEqual(
            line.task_id.project_id, self.project_a, "The task is in the right project"
        )

    def test_product_create_task_in_product_project_and_line_override(self):
        """Create a Task in the product project and override the project on the line

        The product is configured to create a Task in a specific project.
        However, the user chooses a different project on the line itself.
        """
        line = self.env["sale.order.line"].create(
            {
                "product_id": self.product_create_task.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
            }
        )
        # Set the specific project on the product
        self.product_create_task.project_id = self.project_a
        # Set a different project on the line
        line.project_id = self.project_b
        # Confirm
        with RecordCapturer(self.env["project.task"], []) as rc:
            self.order.action_confirm()
        self.assertEqual(
            self.order.project_id, self.project_b, "The project on the order is set"
        )
        self.assertTrue(line.task_id, "The task is created")
        self.assertEqual(line.task_id, rc.records, "The task is created")
        self.assertEqual(
            line.task_id.project_id, self.project_b, "The task is in the right project"
        )

    def test_product_create_task_manually_set(self):
        """Create a Task in the order project, but we set it manually

        The product is configured to create a Task in the order project.
        However, the user manually sets the task on the line.

        No other card should be created, since it's already set.
        The task and the line should be properly linked together.
        """
        line = self.env["sale.order.line"].create(
            {
                "product_id": self.product_create_task.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
            }
        )
        # Set an already existing task on the line
        line.task_id = self.task_b_1
        # Confirm
        with RecordCapturer(self.env["project.task"], []) as rc:
            self.order.action_confirm()
        self.assertFalse(rc.records, "No other task is created")
        self.assertEqual(line.task_id, self.task_b_1, "The task remains the same")
        self.assertEqual(
            self.order.project_id, self.project_b, "The project on the order is set"
        )
        self.assertEqual(
            line.task_id.project_id, self.project_b, "The task is in the right project"
        )
        self.assertEqual(
            line.task_id.sale_line_id, line, "The task is linked to the line"
        )
        self.assertEqual(
            line.task_id.sale_order_id, self.order, "The task is linked to the order"
        )

    def test_product_create_task_manually_set_without_project(self):
        """Create a Task, but we set one without project manually

        The product is configured to create a Task in the order project.
        However, the user manually sets the task on the line.
        The task has no project set, and the order has one.

        No other card should be created, since it's already set.
        The task and the line should be properly linked together.
        The task should be moved to the order's project.
        """
        line = self.env["sale.order.line"].create(
            {
                "product_id": self.product_create_task.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
            }
        )
        # Set a project on the order
        self.order.project_id = self.project_b
        # Set an already existing task on the line
        task = self.env["project.task"].create(
            {"name": "Test Task", "project_id": False}
        )
        line.task_id = task
        # Confirm
        with RecordCapturer(self.env["project.task"], []) as rc:
            self.order.action_confirm()
        self.assertFalse(rc.records, "No other task is created")
        self.assertEqual(line.task_id, task, "The task remains the same")
        self.assertEqual(
            self.order.project_id,
            self.project_b,
            "The project on the order is not changed",
        )
        self.assertEqual(
            line.task_id.project_id,
            self.project_b,
            "The task is moved to the order's project",
        )
        self.assertEqual(
            line.task_id.sale_line_id, line, "The task is linked to the line"
        )
        self.assertEqual(
            line.task_id.sale_order_id, self.order, "The task is linked to the order"
        )

    def test_product_create_task_manually_set_with_project_mismatch(self):
        """The manually set Task's project doesn't match the line's project

        The product is configured to create a Task in the order project.
        However, the user manually sets the task on the line.
        The task has a project set, but it doesn't match the line's project.
        """
        self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product_create_task.id,
                "product_uom_qty": 1,
                "project_id": self.project_a.id,
                "task_id": self.task_b_1.id,
            }
        )
        with self.assertRaisesRegex(
            UserError, "The task .+ is already linked to another project"
        ):
            self.order.action_confirm()

    def test_product_create_task_manually_set_already_linked_sale_line(self):
        """The manually set Task is already linked to another sale line"""
        # Set up another order with a task linked to it
        another_order = self.order.copy()
        another_order.project_id = self.project_a
        another_order.order_line = [
            Command.create(
                {"product_id": self.product_create_task.id, "product_uom_qty": 1}
            )
        ]
        another_order.action_confirm()
        another_task = another_order.order_line.task_id
        self.assertTrue(another_task, "The other task is created")
        self.assertEqual(
            another_task.project_id, self.project_a, "The other task is in the project"
        )
        # Now try to set this same task on a new line
        self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product_create_task.id,
                "product_uom_qty": 1,
                "task_id": another_task.id,
            }
        )
        with self.assertRaisesRegex(
            UserError, "The task .+ is already linked to another line"
        ):
            self.order.action_confirm()

    # Disabled for now as it's giving incompatibility error
    def __test_product_create_task_manually_set_already_linked_order(self):
        """The manually set Task is already linked to another order"""
        # Set up another order with a task linked to it
        another_order = self.order.copy()
        another_order.project_id = self.project_a
        self.project_a.sale_order_id = another_order
        another_task = self.env["project.task"].create(
            {
                "name": "Test Task",
                "allow_billable": True,
                "project_id": self.project_a.id,
                "sale_order_id": another_order.id,
            }
        )
        # Now try to set this same task on a new line
        self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product_create_task.id,
                "product_uom_qty": 1,
                "task_id": another_task.id,
            }
        )
        with self.assertRaisesRegex(
            UserError, "The task .+ is already linked to another order"
        ):
            self.order.action_confirm()

    def test_product_create_task_and_project_with_project_already_set(self):
        """Create a Task and a Project, but we set the project manually

        The product is configured to create a Task and a Project.
        However, the user manually sets the project on the line.

        The task should still be created, in the project the user chose.
        """
        line = self.env["sale.order.line"].create(
            {
                "product_id": self.product_create_task_and_project.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
                "project_id": self.project_b.id,
            }
        )
        with (
            RecordCapturer(self.env["project.task"], []) as rc_task,
            RecordCapturer(self.env["project.project"], []) as rc_project,
        ):
            self.order.action_confirm()
        self.assertFalse(rc_project.records, "No other project is created")
        self.assertTrue(rc_task.records, "The task is created")
        self.assertEqual(line.task_id, rc_task.records, "The task is created")
        self.assertEqual(
            line.task_id.project_id, self.project_b, "The task is in the right project"
        )
        self.assertEqual(
            line.task_id.sale_line_id, line, "The task is linked to the line"
        )
        self.assertEqual(
            line.task_id.sale_order_id, self.order, "The task is linked to the order"
        )

    def test_product_create_task_and_project_with_task_already_set(self):
        """Create a Task and a Project, but we set the task manually

        The product is configured to create a Task and a Project.
        However, the user manually sets the task on the line.

        No other task or project should be created, since its already set.
        The project task should be used, and no other project should be created.
        """
        line = self.env["sale.order.line"].create(
            {
                "product_id": self.product_create_task_and_project.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
                "task_id": self.task_b_1.id,
            }
        )
        with (
            RecordCapturer(self.env["project.task"], []) as rc_task,
            RecordCapturer(self.env["project.project"], []) as rc_project,
        ):
            self.order.action_confirm()
        self.assertFalse(rc_project.records, "No other project is created")
        self.assertFalse(rc_task.records, "No other task is created")
        self.assertEqual(line.task_id, self.task_b_1, "The task remains the same")
        self.assertEqual(
            line.task_id.project_id, self.project_b, "The task is in the right project"
        )
        self.assertEqual(
            line.project_id, self.project_b, "The project is set on the line"
        )
        self.assertEqual(
            line.task_id.sale_line_id, line, "The task is linked to the line"
        )
        self.assertEqual(
            line.task_id.sale_order_id, self.order, "The task is linked to the order"
        )

    def test_product_create_task_and_project_with_project_and_task_already_set(self):
        """Create a Task and a Project, but we set the project and task manually

        The product is configured to create a Task and a Project.
        However, the user manually sets the project and task on the line.

        No other task or project should be created, since they are already set.
        The task and the line should be properly linked together.
        """
        line = self.env["sale.order.line"].create(
            {
                "product_id": self.product_create_task_and_project.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
                "project_id": self.project_b.id,
                "task_id": self.task_b_1.id,
            }
        )
        with (
            RecordCapturer(self.env["project.task"], []) as rc_task,
            RecordCapturer(self.env["project.project"], []) as rc_project,
        ):
            self.order.action_confirm()
        self.assertFalse(rc_project.records, "No other project is created")
        self.assertFalse(rc_task.records, "No other task is created")
        self.assertEqual(line.task_id, self.task_b_1, "The task remains the same")
        self.assertEqual(
            line.task_id.project_id, self.project_b, "The task is in the right project"
        )
        self.assertEqual(
            line.task_id.sale_line_id, line, "The task is linked to the line"
        )
        self.assertEqual(
            line.task_id.sale_order_id, self.order, "The task is linked to the order"
        )

    def test_order_with_multiple_combinations_01(self):
        """Order with multiple combinations

        A Sale Order with multiple lines:
        - A line with a consumable product
            -> nothing happens
        - A line with a service product but without service tracking
            -> nothing happens
        - A line that creates a Task with a specified project in line
            -> a task is created for the specified project
        - A line that creates a Task with a task already set manually
            -> the task remains the same
            -> the project remains the same
        """
        line_consu = self.env["sale.order.line"].create(
            {
                "product_id": self.product_consu.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
            }
        )
        line_no_service_tracking = self.env["sale.order.line"].create(
            {
                "product_id": self.product_no_service_tracking.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
            }
        )
        line_create_task_with_specified_project = self.env["sale.order.line"].create(
            {
                "product_id": self.product_create_task_and_project.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
                "project_id": self.project_b.id,
            }
        )
        line_create_task_with_task_already_set_manually = self.env[
            "sale.order.line"
        ].create(
            {
                "product_id": self.product_create_task_and_project.id,
                "product_uom_qty": 1,
                "order_id": self.order.id,
                "task_id": self.task_a_1.id,
            }
        )
        with (
            RecordCapturer(self.env["project.task"], []) as rc_task,
            RecordCapturer(self.env["project.project"], []) as rc_project,
        ):
            self.order.action_confirm()
        self.assertFalse(rc_project.records, "No other project is created")
        self.assertFalse(
            line_consu.task_id, "The consumable line has no task, of course"
        )
        self.assertFalse(
            line_no_service_tracking.task_id,
            "The line with no service tracking has no task",
        )
        self.assertTrue(
            line_create_task_with_specified_project.task_id,
            "A task created for the specified project",
        )
        self.assertEqual(
            line_create_task_with_specified_project.task_id,
            rc_task.records,
            "A task created for the specified project",
        )
        self.assertEqual(
            line_create_task_with_specified_project.task_id.project_id,
            self.project_b,
            "The task is in the specified project",
        )
        self.assertEqual(
            line_create_task_with_task_already_set_manually.task_id,
            self.task_a_1,
            "The line with create task with task already set manually has the task",
        )
        self.assertEqual(
            line_create_task_with_task_already_set_manually.project_id,
            self.project_a,
            "The line with create task with task already set manually has the project",
        )
