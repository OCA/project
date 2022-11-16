# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestProjectSaleLink(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.company = self.env.ref("base.main_company")
        self.sale_model = self.env["sale.order"]
        self.partner = self.env["res.partner"].create({"name": "test"})
        self.Product = self.env["product.product"]
        self.product = self.Product.create({"name": "test", "type": "service"})
        self.sale_invoice_wizard = self.env["sale.advance.payment.inv"]
        self.reverse_wizard = self.env["account.move.reversal"]

    def test_create_so(self):
        project_pigs = self.env["project.project"].create(
            {
                "name": "Pigs",
                "privacy_visibility": "employees",
                "alias_name": "project+pigs",
                "company_id": self.company.id,
            }
        )
        so = Form(self.env["sale.order"])
        so.partner_id = self.partner
        so.project_id = project_pigs
        with so.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 1.0
            line.price_unit = 100.0
        sale_order = so.save()
        project_pigs.action_open_sale_orders()
        self.assertEqual(project_pigs.sale_order_count, 1)
        sale_order.action_confirm()
        with Form(self.sale_invoice_wizard.with_context(active_ids=[so.id])) as wizard:
            wizard.advance_payment_method = "fixed"
            wizard.fixed_amount = 10.0
        wizard = wizard.save()
        wizard.create_invoices()
        self.assertEqual(project_pigs.customer_invoice_count, 1)
        invoice = sale_order.invoice_ids
        invoice.action_post()
        with Form(
            self.reverse_wizard.with_context(
                active_model="account.move", active_ids=[invoice.id]
            )
        ) as wizard:
            wizard.date = fields.date.today()
            wizard.reason = "no reason"
            wizard.refund_method = "refund"
        wizard = wizard.save()
        wizard.reverse_moves()
        self.assertEqual(project_pigs.customer_invoice_count, 2)
        with Form(self.sale_invoice_wizard.with_context(active_ids=[so.id])) as wizard:
            wizard.advance_payment_method = "fixed"
            wizard.fixed_amount = 10.0
        wizard = wizard.save()
        wizard.create_invoices()
        project_pigs.action_open_customer_invoice()
        self.assertEqual(project_pigs.customer_invoice_count, 3)
