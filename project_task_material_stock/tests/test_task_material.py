# Copyright 2015 Tecnativa - Sergio Teruel
# Copyright 2015 Tecnativa - Carlos Dauden
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common
from odoo.exceptions import UserError


@common.at_install(False)
@common.post_install(True)
class TestTaskMaterial(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestTaskMaterial, cls).setUpClass()

        cls.company = cls.env["res.company"].browse([1])
        cls.stage_deployed = cls.env["project.task.type"].create(
            {"name": "State Deployed example"}
        )
        cls.stage_deployed.consume_material = True
        cls.project = cls.env["project.project"].create({"name": "Project example"})
        cls.product1_uom = cls.env.ref("uom.product_uom_unit")
        cls.product2_uom = cls.env.ref("uom.product_uom_kgm")
        product_obj = cls.env["product.product"]
        cls.product1 = product_obj.create(
            {
                "name": "Product example #1",
                "uom_id": cls.product1_uom.id,
                "uom_po_id": cls.product1_uom.id,
                "company_id": cls.company.id,
            }
        )
        cls.product2 = product_obj.create(
            {
                "name": "Product example #2",
                "uom_id": cls.product2_uom.id,
                "uom_po_id": cls.product2_uom.id,
                "company_id": cls.company.id,
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "task test 1",
                "project_id": cls.project.id,
                "analytic_account_id": cls.env["account.analytic.account"]
                .search([], limit=1)
                .id,
            }
        )
        cls.task_material = cls.env["project.task.material"].create(
            {
                "task_id": cls.task.id,
                "product_id": cls.product1.id,
                "product_uom_id": cls.product1_uom.id,
                "quantity": 3,
            }
        )
        cls.product1.product_tmpl_id.standard_price = 100.0
        cls.expected_amount = -(100.0 * 3)

    def test_task_material(self):

        self.assertEqual(self.task_material.product_uom_id.id, self.product1_uom.id)
        self.task.material_ids.write({"product_id": self.product2.id})
        self.task_material._onchange_product_id()
        self.assertEqual(self.task_material.product_uom_id.id, self.product2_uom.id)
        self.task_material.write({"product_id": self.product1.id})
        result_onchange = self.task_material._onchange_product_id()
        self.assertEqual(
            result_onchange["domain"]["product_uom_id"],
            [("category_id", "=", self.product1_uom.id)],
        )
        self.assertEqual(self.task.stock_state, "pending")
        self.task.stage_id = self.env.ref("project.project_stage_0").id
        self.assertEqual(len(self.task.stock_move_ids), 0)
        self.assertEqual(len(self.task.analytic_line_ids), 0)
        self.task.stage_id = self.stage_deployed.id
        self.assertEqual(len(self.task.stock_move_ids), 1)
        self.task2 = self.task.copy()
        self.assertEqual(len(self.task2.stock_move_ids), 0)
        self.assertEqual(len(self.task2.analytic_line_ids), 0)
        self.task_material2 = self.env["project.task.material"].create(
            {
                "task_id": self.task2.id,
                "product_id": self.product1.id,
                "product_uom_id": self.product1_uom.id,
                "quantity": 3,
            }
        )
        self.task2.stage_id = self.stage_deployed.id
        self.task2.stock_move_ids.write({"state": "draft"})
        self.assertEqual(len(self.task2.stock_move_ids), 1)
        self.assertEqual(len(self.task2.analytic_line_ids), 1)
        moves = self.task2.stock_move_ids.ids
        analytics = self.task2.analytic_line_ids.ids
        self.task2.unlink()
        self.assertEqual(len(self.env["stock.move"].search([("id", "in", moves)])), 0)
        self.assertEqual(
            len(self.env["account.analytic.line"].search([("id", "in", analytics)])), 0
        )
        self.task.stock_move_ids.write({"state": "confirmed"})
        self.assertEqual(self.task.stock_state, "confirmed")
        self.assertEqual(len(self.task.analytic_line_ids), 1)
        with self.assertRaises(UserError):
            self.task.stage_id = self.env.ref("project.project_stage_0").id
        self.task.stage_id = self.stage_deployed.id
        analytic_line = self.task.analytic_line_ids[0]
        self.assertAlmostEqual(analytic_line.amount, self.expected_amount)
        self.task.action_assign()
        self.assertEqual(self.task.stock_state, "assigned")
        self.assertEqual(len(self.task.stock_move_ids), 1)
        self.task.stock_move_ids[:1].move_line_ids.qty_done = self.task.stock_move_ids[
            :1
        ].move_line_ids.product_qty
        self.task.action_done()
        self.assertEqual(self.task.stock_state, "done")
        self.assertRaises(Exception, self.task.unlink)
        self.assertRaises(Exception, self.task_material.unlink)
