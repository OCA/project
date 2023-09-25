# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.project_stock.tests.common import TestProjectStockBase


class TestProjectStockAnalyticTag(TestProjectStockBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_stock_quant(cls, cls.product_a, cls.location, 2)
        cls._create_stock_quant(cls, cls.product_b, cls.location, 1)
        cls._create_stock_quant(cls, cls.product_c, cls.location, 1)
        cls.task = cls._create_task(cls, [(cls.product_a, 2), (cls.product_b, 1)])
        cls.move_product_a = cls.task.move_ids.filtered(
            lambda x: x.product_id == cls.product_a
        )
        cls.move_product_b = cls.task.move_ids.filtered(
            lambda x: x.product_id == cls.product_b
        )
        aa_tag_model = cls.env["account.analytic.tag"]
        cls.analytic_tag_1 = aa_tag_model.create({"name": "Test tag 1"})
        cls.analytic_tag_2 = aa_tag_model.create({"name": "Test tag 2"})

    def _create_stock_quant(self, product, location, qty):
        self.env["stock.quant"].create(
            {"product_id": product.id, "location_id": location.id, "quantity": qty}
        )

    def test_project_stock_analytic_tag_01(self):
        self.task = self.env["project.task"].browse(self.task.id)
        self.task.write({"stage_id": self.stage_done.id})
        self.task.action_done()
        tags = self.task.mapped("stock_analytic_line_ids.tag_ids")
        self.assertNotIn(self.analytic_tag_1, tags)
        self.assertNotIn(self.analytic_tag_2, tags)

    def test_project_stock_analytic_tag_02(self):
        self.task.stock_analytic_tag_ids = self.analytic_tag_1 + self.analytic_tag_2
        self.task = self.env["project.task"].browse(self.task.id)
        self.task.write({"stage_id": self.stage_done.id})
        self.task.action_done()
        tags = self.task.mapped("stock_analytic_line_ids.tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertIn(self.analytic_tag_2, tags)

    def test_project_stock_analytic_tag_03(self):
        self.task.stock_analytic_tag_ids = self.analytic_tag_1
        self.task = self.env["project.task"].browse(self.task.id)
        self.task.write({"stage_id": self.stage_done.id})
        self.task.action_done()
        tags = self.task.mapped("stock_analytic_line_ids.tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertNotIn(self.analytic_tag_2, tags)
