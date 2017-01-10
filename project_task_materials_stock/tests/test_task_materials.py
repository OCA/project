# -*- coding: utf-8 -*-
# Copyright 2015 Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2015 Antiun Ingeniería S.L. - Carlos Dauden
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp.exceptions import UserError

from openerp.tests.common import TransactionCase


class TestTaskMaterials(TransactionCase):
    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestTaskMaterials, self).setUp()
        self.stage_deployed = self.env.ref('project.project_stage_1')
        self.stage_deployed.consume_material = True
        self.project = self.env.ref('project.project_project_1')
        self.product1 = self.env.ref('product.product_product_40')
        self.product2 = self.env.ref('stock.product_icecream')
        self.product1_uom = self.env.ref('product.product_uom_unit')
        self.product2_uom = self.env.ref('product.product_uom_kgm')
        self.task = self.env['project.task'].create(
            {'name': 'task test 1',
             'project_id': self.project.id})
        self.task_materials = self.env['project.task.materials'].create(
            {'task_id': self.task.id,
             'product_id': self.product1.id,
             'product_uom_id': self.product1_uom.id,
             'quantity': 3})
        self.product1.product_tmpl_id.standard_price = 100.0
        self.expected_amount = -(100.0 * 3)

    def test_task_materials(self):

        self.assertEqual(self.task_materials.product_uom_id.id,
                         self.product1_uom.id)
        self.task.material_ids.write({'product_id': self.product2.id})
        self.task_materials._onchange_product_id()
        self.assertEqual(self.task_materials.product_uom_id.id,
                         self.product2_uom.id)
        self.task_materials.write({'product_id': self.product1.id})
        result_onchange = self.task_materials._onchange_product_id()
        self.assertEqual(result_onchange['domain']['product_uom_id'],
                         [('category_id', '=', self.product1_uom.id)])
        self.assertEqual(self.task.stock_state, 'pending')
        self.task.stage_id = self.env.ref('project.project_stage_0').id
        self.assertEqual(len(self.task.stock_move_ids), 0)
        self.assertEqual(len(self.task.analytic_line_ids), 0)
        self.task.stage_id = self.stage_deployed.id
        self.assertEqual(len(self.task.stock_move_ids), 1)
        self.task2 = self.task.copy()
        self.task_materials2 = self.env['project.task.materials'].create(
            {'task_id': self.task2.id,
             'product_id': self.product1.id,
             'product_uom_id': self.product1_uom.id,
             'quantity': 3})
        self.task2.stage_id = self.stage_deployed.id
        self.task2.stock_move_ids.write({'state': 'draft'})
        self.assertEqual(len(self.task2.stock_move_ids), 1)
        self.assertEqual(len(self.task2.analytic_line_ids), 1)
        moves = self.task2.stock_move_ids.ids
        analytics = self.task2.analytic_line_ids.ids
        self.task2.unlink()
        self.assertEqual(
            len(self.env['stock.move'].search([('id', 'in', moves)])), 0)
        self.assertEqual(
            len(self.env['account.analytic.line'].search(
                [('id', 'in', analytics)])), 0)
        self.task.stock_move_ids.write({'state': 'confirmed'})
        self.assertEqual(self.task.stock_state, 'confirmed')
        self.assertEqual(len(self.task.analytic_line_ids), 1)
        with self.assertRaises(UserError):
            self.task.stage_id = self.env.ref('project.project_stage_0').id
        self.task.stage_id = self.stage_deployed.id
        analytic_line = self.task.analytic_line_ids[0]
        self.assertAlmostEqual(analytic_line.amount, self.expected_amount)
        self.task.action_assign()
        self.assertEqual(self.task.stock_state, 'assigned')
        self.task.action_done()
        self.assertEqual(self.task.stock_state, 'done')
        self.assertRaises(Exception, self.task.unlink)
