# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.tests.common import SavepointCase


class TestTaskMaterialAnalyticPartner(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestTaskMaterialAnalyticPartner, cls).setUpClass()

        cls.stage_deployed = cls.env['project.task.type'].create({
            'name': 'Stage Deployment',
        })
        cls.stage_analysis = cls.env['project.task.type'].create({
            'name': 'State Analysis',
        })
        cls.stage_deployed.consume_material = True
        cls.product = cls.env['product.product'].create({
            'name': 'Product #1',
        })
        cls.project = cls.env['project.project'].create({
            'name': 'Project #1'
        })
        cls.partner1 = cls.env['res.partner'].create({
            'name': 'Partner #2',
        })
        cls.partner2 = cls.env['res.partner'].create({
            'name': 'Partner #12',
        })
        cls.task = cls.env['project.task'].create({
            'name': 'Task Test 1',
            'project_id': cls.project.id
        })
        cls.task_material = cls.env['project.task.material'].create({
            'task_id': cls.task.id,
            'product_id': cls.product.id,
            'quantity': 3.0,
            'other_partner_id': cls.partner1.id,
        })

    def test_task_material_analytic_partner(self):
        self.task.stage_id = self.stage_deployed.id
        self.assertEqual(self.task_material.analytic_line_id.other_partner_id,
                         self.partner1)
        with self.assertRaises(UserError):
            self.task.stage_id = self.stage_analysis
        self.task_material.other_partner_id = self.partner2
        self.task.stage_id = self.stage_deployed.id
        self.assertEqual(self.task_material.analytic_line_id.other_partner_id,
                         self.partner2)
