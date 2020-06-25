# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

# from odoo.osv import expression
from odoo.tests import common

# from odoo.tools.safe_eval import safe_eval


class TestProjectPurchaseUtilities(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProjectPurchaseUtilities, cls).setUpClass()
        cls.project_model = cls.env["project.project"]
        cls.project = cls.project_model.create({"name": "Test Project"})
        cls.purchase_model = cls.env["purchase.order"]
        cls.purchase = cls.purchase_model.search(
            [("state", "in", ("draft", "sent")), ("order_line", "!=", False)], limit=1
        )
        cls.invoice_model = cls.env["account.move"]
        cls.invoice_line_model = cls.env["account.move.line"]

    def test_project_purchase(self):
        self.assertTrue(self.purchase)
        self.purchase.write({"invoice_status": "to invoice"})
        self.assertFalse(self.project.purchase_count)
        self.assertFalse(self.project.purchase_line_total)
        self.assertFalse(self.project.purchase_invoice_count)
        self.assertFalse(self.project.purchase_invoice_line_total)
        self.purchase.order_line[:1].write(
            {
                "account_analytic_id": self.project.analytic_account_id.id,
                "price_unit": 50,
                "product_qty": 4,
                "qty_received": 4,
            }
        )
        self.project.invalidate_cache()
        self.assertEquals(self.project.purchase_count, 1)
        self.assertEquals(self.project.purchase_line_total, 200)
        self.assertFalse(self.project.purchase_invoice_count)
        self.assertFalse(self.project.purchase_invoice_line_total)
        self.purchase.button_confirm()
        invoice = self.invoice_model.create(
            {
                "partner_id": self.purchase.partner_id.id,
                "purchase_id": self.purchase.id,
                "type": "in_invoice",
            }
        )
        for line in self.purchase.order_line:
            categ_id = line.product_id.categ_id
            account_id = categ_id.property_account_expense_categ_id.id
            vals = {
                "move_id": invoice.id,
                "name": line.name,
                "account_id": account_id,
                "analytic_account_id": line.account_analytic_id.id,
            }
            self.invoice_line_model.create(vals)
        self.project.invalidate_cache()
        self.assertEquals(self.project.purchase_invoice_count, 1)
        purchase_domain = [
            (
                "account_analytic_id",
                "in",
                self.project.mapped("analytic_account_id").ids,
            )
        ]
        lines = self.env["purchase.order.line"].search(purchase_domain)
        order_domain = [("id", "in", lines.mapped("order_id").ids)]
        purchase_dict = self.project.button_open_purchase_order()
        self.assertEquals(purchase_dict.get("domain"), order_domain)
        purchase_line_dict = self.project.button_open_purchase_order_line()
        self.assertEquals(purchase_line_dict.get("domain"), purchase_domain)
