# Copyright 2026 Innovara Ltd - Manuel Fombuena
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestProjectCostsRevenues(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.report = cls.env["project.costs.revenues"]
        cls.hour_uom = cls.env.ref("uom.product_uom_hour")
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Test Worker", "hourly_cost": 60.0}
        )
        # Service product billed on delivered timesheets, creating its own
        # project + task when the sale order is confirmed.
        cls.product = cls.env["product.product"].create(
            {
                "name": "Consulting",
                "type": "service",
                "invoice_policy": "delivery",
                "service_type": "timesheet",
                "service_tracking": "task_in_project",
                "list_price": 100.0,
                "standard_price": 60.0,
                "uom_id": cls.hour_uom.id,
                "uom_po_id": cls.hour_uom.id,
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product.id, "product_uom_qty": 10.0})
                ],
            }
        )
        cls.sale_order.action_confirm()
        cls.so_line = cls.sale_order.order_line
        cls.project = cls.so_line.project_id
        cls.task = cls.so_line.task_id
        cls.timesheet = cls.env["account.analytic.line"].create(
            {
                "name": "Work done",
                "project_id": cls.project.id,
                "task_id": cls.task.id,
                "employee_id": cls.employee.id,
                "unit_amount": 4.0,
            }
        )

    def _rows(self):
        return self.report.search([("project_id", "=", self.project.id)])

    def test_duration_matches_logged_hours(self):
        self.assertEqual(sum(self._rows().mapped("timesheet_duration")), 4.0)

    def test_cost_is_negative_and_proportional(self):
        # 4 hours * 60.0 hourly cost, stored negative
        self.assertAlmostEqual(
            sum(self._rows().mapped("timesheet_cost")), -240.0, places=2
        )

    def test_amount_to_invoice_before_invoicing(self):
        # 4 logged hours * 100.0 sale price, nothing invoiced yet
        rows = self._rows()
        self.assertAlmostEqual(sum(rows.mapped("amount_to_invoice")), 400.0, places=2)
        self.assertEqual(sum(rows.mapped("amount_invoiced")), 0.0)

    def test_amount_moves_to_invoiced_after_invoicing(self):
        self.sale_order._create_invoices()
        self.sale_order.invoice_ids.action_post()
        rows = self._rows()
        self.assertEqual(sum(rows.mapped("amount_to_invoice")), 0.0)
        self.assertAlmostEqual(sum(rows.mapped("amount_invoiced")), 400.0, places=2)

    def test_non_timesheet_line_is_excluded(self):
        # An analytic line with no project must not surface in the report.
        plan = self.env["account.analytic.plan"].create({"name": "Test Plan"})
        account = self.env["account.analytic.account"].create(
            {"name": "Test Analytic Account", "plan_id": plan.id}
        )
        self.env["account.analytic.line"].create(
            {"name": "Misc cost", "account_id": account.id, "amount": -50.0}
        )
        self.assertFalse(self.report.search([("account_id", "=", account.id)]))
