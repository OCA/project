# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.tests.common import BaseCommon


class TestProjectPurchaseUtilities(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.project_model = cls.env["project.project"]
        cls.project = cls.project_model.create({"name": "Test Project"})
        cls.purchase_model = cls.env["purchase.order"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Product 4",
                "standard_price": 500.0,
                "list_price": 750.0,
                "type": "consu",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.purchase = cls.purchase_model.create(
            {
                "partner_id": cls.partner.id,
            }
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
        self.purchase.write(
            {
                "order_line": [
                    Command.create(
                        {
                            "name": "Test line",
                            "analytic_distribution": {self.project.account_id.id: 100},
                            "price_unit": 50,
                            "product_qty": 4,
                            "qty_received": 4,
                            "product_uom": self.product.uom_id.id,
                            "product_id": self.product.id,
                        }
                    )
                ]
            }
        )

        self.env.invalidate_all()

        self.assertEqual(self.project.purchase_count, 1)
        self.assertEqual(self.project.purchase_line_total, 200)
        self.assertFalse(self.project.purchase_invoice_count)
        self.assertFalse(self.project.purchase_invoice_line_total)
        self.purchase.button_confirm()
        invoice = self.invoice_model.create(
            {
                "partner_id": self.purchase.partner_id.id,
                "purchase_id": self.purchase.id,
                "move_type": "in_invoice",
            }
        )
        for line in self.purchase.order_line:
            categ_id = line.product_id.categ_id
            account_id = categ_id.property_account_expense_categ_id.id
            vals = {
                "move_id": invoice.id,
                "name": line.name,
                "account_id": account_id,
                "analytic_distribution": line.analytic_distribution,
            }
            self.invoice_line_model.create(vals)
        self.env.invalidate_all()
        self.assertEqual(self.project.purchase_invoice_count, 1)

        purchase_domain = self.project._domain_purchase_order_line()

        lines = self.env["purchase.order.line"].search(purchase_domain)
        order_domain = [("id", "in", lines.mapped("order_id").ids)]
        purchase_dict = self.project.button_open_purchase_order()
        self.assertEqual(purchase_dict.get("domain"), order_domain)
        purchase_line_dict = self.project.button_open_purchase_order_line()
        self.assertEqual(purchase_line_dict.get("domain"), purchase_domain)

        action = self.env.ref("account.action_move_in_invoice_type")
        invoice_domain = expression.AND(
            [safe_eval(action.domain or "[]"), self.project._domain_purchase_invoice()]
        )  # only one test invoice (line)

        invoice_dict = self.project.button_open_purchase_invoice()
        self.assertEqual(invoice_dict.get("domain"), invoice_domain)

        invoice_line_domain = self.project._domain_purchase_invoice_line()

        invoice_line_dict = self.project.button_open_purchase_invoice_line()
        self.assertEqual(invoice_line_dict.get("domain"), invoice_line_domain)
