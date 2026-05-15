# Copyright 2026 ForgeFlow S.L.
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.tests import tagged

from .common import ProjectReferenceCommon


@tagged("post_install", "-at_install")
class TestCustomerReference(ProjectReferenceCommon):
    # ------------------------------------------------------------------
    # Task create → SO
    # ------------------------------------------------------------------

    def test_task_create_sets_so_ref(self):
        """Creating a task with customer_reference populates SO's client_order_ref."""
        self._make_task(customer_reference="REF-001")
        self.assertEqual(self.order.client_order_ref, "REF-001")

    def test_task_create_overwrites_so_ref(self):
        """Creating a task with customer_reference overwrites an existing SO ref."""
        self.order.client_order_ref = "OLD-REF"
        self._make_task(customer_reference="NEW-REF")
        self.assertEqual(self.order.client_order_ref, "NEW-REF")

    def test_task_create_no_ref_leaves_so_unchanged(self):
        """Creating a task without customer_reference leaves SO's ref intact."""
        self.order.client_order_ref = "KEEP-ME"
        self._make_task()
        self.assertEqual(self.order.client_order_ref, "KEEP-ME")

    # ------------------------------------------------------------------
    # Task write → SO
    # ------------------------------------------------------------------

    def test_task_write_updates_so_ref(self):
        """Writing customer_reference on a task updates SO's client_order_ref."""
        task = self._make_task()
        task.customer_reference = "REF-002"
        self.assertEqual(self.order.client_order_ref, "REF-002")

    def test_task_write_overwrites_existing_so_ref(self):
        """Writing customer_reference on a task overwrites an existing SO ref."""
        self.order.client_order_ref = "OLD"
        task = self._make_task()
        task.customer_reference = "NEW"
        self.assertEqual(self.order.client_order_ref, "NEW")

    def test_task_write_no_ref_leaves_so_unchanged(self):
        """Writing an unrelated field on a task does not touch SO's ref."""
        self.order.client_order_ref = "UNCHANGED"
        task = self._make_task()
        task.write({"name": "Renamed Task"})
        self.assertEqual(self.order.client_order_ref, "UNCHANGED")

    # ------------------------------------------------------------------
    # SO write → Task
    # ------------------------------------------------------------------

    def test_so_write_updates_task_ref(self):
        """Writing client_order_ref on an SO updates all linked tasks."""
        task = self._make_task()
        self.order.client_order_ref = "SO-REF-001"
        self.assertEqual(task.customer_reference, "SO-REF-001")

    def test_so_write_updates_multiple_tasks(self):
        """Writing client_order_ref updates every task linked to the SO."""
        task1 = self._make_task(name="Task 1")
        task2 = self._make_task(name="Task 2")
        self.order.client_order_ref = "BATCH-REF"
        self.assertEqual(task1.customer_reference, "BATCH-REF")
        self.assertEqual(task2.customer_reference, "BATCH-REF")

    def test_so_write_no_ref_leaves_tasks_unchanged(self):
        """Writing an unrelated field on SO does not touch task's ref."""
        task = self._make_task(customer_reference="KEEP")
        self.order.write({"note": "Some note"})
        self.assertEqual(task.customer_reference, "KEEP")

    # ------------------------------------------------------------------
    # No infinite loop
    # ------------------------------------------------------------------

    def test_no_infinite_loop_task_then_so(self):
        """Setting customer_reference on a task does not trigger recursion."""
        task = self._make_task()
        task.customer_reference = "LOOP-A"
        self.assertEqual(self.order.client_order_ref, "LOOP-A")
        self.assertEqual(task.customer_reference, "LOOP-A")

    def test_no_infinite_loop_so_then_task(self):
        """Setting client_order_ref on an SO does not trigger recursion."""
        task = self._make_task()
        self.order.client_order_ref = "LOOP-B"
        self.assertEqual(task.customer_reference, "LOOP-B")
        self.assertEqual(self.order.client_order_ref, "LOOP-B")

    # ------------------------------------------------------------------
    # _timesheet_create_task_prepare_values (sale_order_line.py)
    # ------------------------------------------------------------------

    def test_timesheet_task_values_copies_so_ref(self):
        """_timesheet_create_task_prepare_values includes client_order_ref."""
        self.order.client_order_ref = "ORDER-REF"
        service = self.env["product.product"].create(
            {"name": "Service", "type": "service", "taxes_id": False}
        )
        line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": service.id,
                "product_uom_qty": 1,
            }
        )
        vals = line._timesheet_create_task_prepare_values(self.project)
        self.assertEqual(vals.get("customer_reference"), "ORDER-REF")

    def test_timesheet_task_values_no_ref_skips_field(self):
        """_timesheet_create_task_prepare_values omits field when SO has no ref."""
        self.order.client_order_ref = False
        service = self.env["product.product"].create(
            {"name": "Service 2", "type": "service", "taxes_id": False}
        )
        line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": service.id,
                "product_uom_qty": 1,
            }
        )
        vals = line._timesheet_create_task_prepare_values(self.project)
        self.assertNotIn("customer_reference", vals)
