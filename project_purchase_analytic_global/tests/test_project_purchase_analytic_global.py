# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date

from odoo.tests.common import Form, TransactionCase


class TestProjectPurchaseAnalyticGlobal(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Project = cls.env["project.project"]
        cls.AnalyticAccount = cls.env["account.analytic.account"]
        cls.Partner = cls.env["res.partner"]
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.partner1 = cls.Partner.create({"name": "Partner1"})
        cls.analytic_account1 = cls.AnalyticAccount.create(
            {"name": "Analytic Account 1"}
        )
        cls.product = cls.env.ref("product.product_product_4")
        cls.project1 = cls.Project.create(
            {
                "name": "Project1",
                "analytic_account_id": cls.analytic_account1.id,
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
            line_form.product_uom = self.product.uom_id
            line_form.date_planned = date.today()
        purchase_form.save()
        self.assertEqual(
            purchase_order.account_analytic_id, self.project1.analytic_account_id
        )
