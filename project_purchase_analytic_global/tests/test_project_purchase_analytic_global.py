# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestProjectPurchaseAnalyticGlobal(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Project = cls.env["project.project"]
        cls.AnalyticPlan = cls.env["account.analytic.plan"]
        cls.AnalyticAccount = cls.env["account.analytic.account"]
        cls.Partner = cls.env["res.partner"]
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.partner1 = cls.Partner.create({"name": "Partner1"})
        cls.analytic_plan = cls.AnalyticPlan.create({"name": "Plan"})
        cls.analytic_account1 = cls.AnalyticAccount.create(
            {"name": "Analytic Account 1", "plan_id": cls.analytic_plan.id}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "list_price": 100.0,
                "standard_price": 50.0,
            }
        )
        cls.project1 = cls.Project.create(
            {
                "name": "Project1",
                "account_id": cls.analytic_account1.id,
            }
        )

    def test_analytic_account(self):
        action = self.project1.action_open_project_purchase_orders()
        self.PurchaseOrder = self.PurchaseOrder.with_context(**action["context"])
        purchase_order = self.PurchaseOrder.create({"partner_id": self.partner1.id})
        purchase_form = Form(purchase_order)
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.name = self.product.name
            line_form.product_qty = 10
            line_form.price_unit = 20
            line_form.date_planned = date.today()
        purchase_form.save()
        self.assertEqual(
            purchase_order.analytic_distribution,
            {str(self.project1.account_id.id): 100.0},
        )

    def test_analytic_account_not_overridden_by_distribution_model(self):
        """The project's analytic distribution must not be overridden by a
        matching analytic distribution model when the purchase order is
        created from the project smart button."""
        other_analytic_account = self.AnalyticAccount.create(
            {"name": "Analytic Account 2", "plan_id": self.analytic_plan.id}
        )
        self.env["account.analytic.distribution.model"].create(
            {
                "partner_id": self.partner1.id,
                "analytic_distribution": {str(other_analytic_account.id): 100.0},
            }
        )
        action = self.project1.action_open_project_purchase_orders()
        self.PurchaseOrder = self.PurchaseOrder.with_context(**action["context"])
        purchase_order = self.PurchaseOrder.create({"partner_id": self.partner1.id})
        purchase_form = Form(purchase_order)
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.name = self.product.name
            line_form.product_qty = 10
            line_form.price_unit = 20
            line_form.date_planned = date.today()
        purchase_form.save()
        self.assertEqual(
            purchase_order.analytic_distribution,
            {str(self.project1.account_id.id): 100.0},
        )
