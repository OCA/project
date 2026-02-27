# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProjectEstimation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        cls.tax_7 = cls.env["account.tax"].create(
            {
                "name": "Tax 7%",
                "amount_type": "percent",
                "amount": 7.0,
                "type_tax_use": "sale",
            }
        )

        # Product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Service",
                "type": "service",
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_unit.id,
                "standard_price": 50.0,
                "list_price": 100.0,
            }
        )

    def test_01_estimation_computations(self):
        """Test subtotal, margin, and total computations on estimation."""
        estimation = self.env["project.estimation"].create(
            {
                "partner_id": self.partner.id,
                "target_margin": 20.0,
                "line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_uom_qty": 2.0,
                            "price_unit": 100.0,
                            "unit_cost": 50.0,
                            "tax_id": [Command.set(self.tax_7.ids)],
                        }
                    )
                ],
            }
        )

        line = estimation.line_ids[0]

        self.assertEqual(line.price_subtotal, 200.0)  # 2 * 100
        self.assertEqual(line.cost_subtotal, 100.0)  # 2 * 50
        self.assertEqual(line.margin, 100.0)  # 200 - 100
        self.assertEqual(line.margin_percent, 0.5)  # 100 / 200 = 50%

        self.assertEqual(estimation.total_cost, 100.0)
        self.assertEqual(estimation.amount_untaxed, 200.0)
        self.assertEqual(estimation.amount_tax, 14.0)  # 200 * 0.07
        self.assertEqual(estimation.amount_total, 214.0)

        self.assertEqual(estimation.total_margin, 100.0)
        self.assertEqual(estimation.total_margin_percent, 0.5)

        # Target expected fields
        # total_cost / (1 - target_margin) -> 100 / (1 - 0.2) = 125
        self.assertEqual(estimation.target_sale_price, 125.0)
        self.assertEqual(estimation.expected_profit, 25.0)

    def test_02_workflow_and_wizard(self):
        """Test estimation workflow and wizard Sale Order generation."""
        estimation = self.env["project.estimation"].create(
            {
                "partner_id": self.partner.id,
                "line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                            "unit_cost": 50.0,
                        }
                    )
                ],
            }
        )

        self.assertEqual(estimation.state, "draft")
        estimation.action_approve()
        self.assertEqual(estimation.state, "approved")

        # Open Wizard
        wizard = (
            self.env["project.estimation.create.sale.order"]
            .with_context(default_estimation_id=estimation.id)
            .create(
                {
                    "estimation_id": estimation.id,
                }
            )
        )

        # Ensure wizard loaded lines properly
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids[0].price_unit, 100.0)

        # Execute wizard
        res = wizard.action_create_sale_order()

        # Check wizard result
        self.assertEqual(res["res_model"], "sale.order")
        self.assertEqual(estimation.state, "won")

        so = self.env["sale.order"].browse(res["res_id"])
        self.assertEqual(so.partner_id, self.partner)
        self.assertEqual(len(so.order_line), 1)
        self.assertEqual(so.order_line[0].price_unit, 100.0)

        # Ensure project was created as requested
        self.assertTrue(estimation.project_id)
        self.assertEqual(estimation.project_id.name, estimation.name)

    def test_03_display_type_no_computations(self):
        """Test section/note lines and ensure they don't break computation."""
        estimation = self.env["project.estimation"].create(
            {
                "partner_id": self.partner.id,
                "line_ids": [
                    Command.create(
                        {
                            "display_type": "line_section",
                            "name": "Section A",
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                            "unit_cost": 50.0,
                        }
                    ),
                ],
            }
        )

        section_line = estimation.line_ids.filtered(
            lambda line: line.display_type == "line_section"
        )
        self.assertTrue(section_line)
        self.assertEqual(section_line.cost_subtotal, 0.0)
        self.assertEqual(section_line.price_subtotal, 0.0)

        # Totals should ignore section line
        self.assertEqual(estimation.total_cost, 50.0)
        self.assertEqual(estimation.amount_untaxed, 100.0)
