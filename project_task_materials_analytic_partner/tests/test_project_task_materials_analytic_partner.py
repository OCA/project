# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestTaskMaterialsAnalyticPartner(TransactionCase):
    def setUp(self):
        super(TestTaskMaterialsAnalyticPartner, self).setUp()

        self.stage_deployed = self.env.ref('project.project_tt_deployment')
        self.stage_analysis = self.env.ref('project.project_tt_analysis')
        self.stage_deployed.consume_material = True
        self.product = self.env.ref('product.product_product_40')
        self.project = self.env.ref('project.project_project_1')
        self.partner1 = self.env.ref('base.res_partner_2')
        self.partner2 = self.env.ref('base.res_partner_12')
        self.factor = self.env.ref(
            'hr_timesheet_invoice.timesheet_invoice_factor1')

        self.task = self.env['project.task'].create({
            'name': 'Task Test 1',
            'project_id': self.project.id
        })
        self.task_materials = self.env['project.task.materials'].create({
            'task_id': self.task.id,
            'product_id': self.product.id,
            'quantity': 3,
            'to_invoice': self.factor.id,
            'other_partner_id': self.partner1.id,
        })

    def test_task_materials_analytic_partner(self):
        self.task.stage_id = self.stage_deployed.id
        self.assertEqual(self.task_materials.analytic_line_id.other_partner_id,
                         self.partner1)
        self.assertEqual(self.task_materials.analytic_line_id.to_invoice,
                         self.factor)

        self.task.stage_id = self.stage_analysis
        self.task_materials.other_partner_id = self.partner2
        self.task_materials.to_invoice = False
        self.task.stage_id = self.stage_deployed.id
        self.assertEqual(self.task_materials.analytic_line_id.other_partner_id,
                         self.partner2)
        self.assertFalse(self.task_materials.analytic_line_id.to_invoice)
