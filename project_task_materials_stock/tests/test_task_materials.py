# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp.tests.common import TransactionCase


class TestTaskMaterials(TransactionCase):
    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestTaskMaterials, self).setUp()
        self.stage_deployed = self.env.ref('project.project_tt_deployment')
        self.stage_deployed.consume_material = True
        self.project = self.env.ref('project.project_project_1')
        # import pdb; pdb.set_trace()
        self.product = self.env.ref('product.product_product_40')
        self.task = self.env['project.task'].create(
            {'name': 'task test 1',
             'project_id': self.project.id})
        self.task_materials = self.env['project.task.materials'].create(
            {'task_id': self.task.id,
             'product_id': self.product.id,
             'quantity': 3})
        self.product.product_tmpl_id.standard_price = 100.0
        self.expected_amount = -(100.0 * 3)

    def test_task_materials(self):
        self.assertEqual(self.task.stock_state, 'pending')
        self.task.stage_id = self.stage_deployed.id
        self.assertEqual(len(self.task.stock_move_ids), 1)
        self.assertEqual(len(self.task.analytic_line_ids), 1)
        self.task.stage_id = self.env.ref('project.project_tt_design').id
        self.assertEqual(len(self.task.stock_move_ids), 0)
        self.assertEqual(len(self.task.analytic_line_ids), 0)
        self.task.stage_id = self.stage_deployed.id
        analytic_line = self.task.analytic_line_ids[0]
        self.assertAlmostEqual(analytic_line.amount, self.expected_amount)
        self.task.action_assign()
        self.assertEqual(self.task.stock_state, 'assigned')
        self.task.action_done()
        self.assertEqual(self.task.stock_state, 'done')
        self.assertRaises(Exception, self.task.unlink)
