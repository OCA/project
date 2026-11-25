# Copyright 2025 Oihane Crucelaegui - AvanzOSC
# Copyright 2025 Mathieu Benoit - TechnoLibre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.tests.common import BaseCommon


class TestProjectSaleUtilities(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.project_model = cls.env["project.project"]
        cls.project = cls.project_model.create({"name": "Test Project"})
        cls.sale_model = cls.env["sale.order"]
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
        cls.sale = cls.sale_model.create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.invoice_model = cls.env["account.move"]
        cls.invoice_line_model = cls.env["account.move.line"]

    def test_project_sale(self):
        self.assertTrue(self.sale)
        self.sale.write({"invoice_status": "to invoice"})
        self.assertFalse(self.project.sale_count)
        self.assertFalse(self.project.sale_line_total)
        self.assertFalse(self.project.sale_invoice_count)
        self.assertFalse(self.project.sale_invoice_line_total)
        self.sale.write(
            {
                "order_line": [
                    Command.create(
                        {
                            "name": "Test line",
                            "analytic_distribution": {self.project.account_id.id: 100},
                            "price_unit": 50,
                            "product_uom_qty": 4,
                            "qty_delivered": 4,
                            "product_uom": self.product.uom_id.id,
                            "product_id": self.product.id,
                        }
                    )
                ]
            }
        )

        self.env.invalidate_all()

        self.assertEqual(self.project.sale_count, 1)
        self.assertEqual(self.project.sale_line_total, 200)
        self.assertFalse(self.project.sale_invoice_count)
        self.assertFalse(self.project.sale_invoice_line_total)
        self.sale.action_confirm()
        invoice = self.invoice_model.create(
            {
                "partner_id": self.sale.partner_id.id,
                "move_type": "out_invoice",
            }
        )
        for line in self.sale.order_line:
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
        self.assertEqual(self.project.sale_invoice_count, 1)

        sale_domain = self.project._domain_sale_order_line()

        lines = self.env["sale.order.line"].search(sale_domain)
        order_domain = [("id", "in", lines.mapped("order_id").ids)]
        sale_dict = self.project.button_open_sale_order()
        self.assertEqual(sale_dict.get("domain"), order_domain)
        sale_line_dict = self.project.button_open_sale_order_line()
        self.assertEqual(sale_line_dict.get("domain"), sale_domain)

        action = self.env.ref("account.action_move_out_invoice_type")
        invoice_domain = expression.AND(
            [safe_eval(action.domain or "[]"), self.project._domain_sale_invoice()]
        )  # only one test invoice (line)

        invoice_dict = self.project.button_open_sale_invoice()
        self.assertEqual(invoice_dict.get("domain"), invoice_domain)

        invoice_line_domain = self.project._domain_sale_invoice_line()

        invoice_line_dict = self.project.button_open_sale_invoice_line()
        self.assertEqual(invoice_line_dict.get("domain"), invoice_line_domain)
