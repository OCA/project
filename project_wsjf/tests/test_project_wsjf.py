# -*- coding: utf-8 -*-
# Copyright (C) 2019  Gabriel Cardoso de Faria - KMEE - www.kmee.com.br
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import common
from odoo.tests.common import tagged


@tagged('post_install')
class TestProjectWSJF(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.project_1 = self.env.ref('project.project_project_data')
        self.project_2 = self.env.ref('project_wsjf.project_project_data_1')
        self.task_1 = self.env.ref('project_wsjf.project_task_data_15')
        self.task_2 = self.env.ref('project_wsjf.project_task_data_16')

    def test_compute_wsjf_value(self):
        self.project_1.write({
            'business_value': 1,
            'time_criticality': 1,
            'risk_reduction': 1,
            'internal_pressure': 8,
            'job_size': 1,
        })
        self.assertEqual(self.project_1.wsjf, 11.0)

    def test_inverse_project_id(self):
        self.project_2.write({
            'business_value': 1,
            'time_criticality': 1,
            'risk_reduction': 2,
            'internal_pressure': 8,
            'job_size': 1,
        })
        task_3 = self.env['project.task'].create({
            'user_id': self.env.ref('base.user_admin').id,
            'priority': '0',
            'project_id': self.project_2.id,
            'active': True,
            'name': 'Testing WSJF prioritization model',
            'stage_id': self.env.ref('project.project_stage_data_2').id,
            'description': 'This task should inherit the WSJF values from '
                           'the project it belongs',
        })
        self.assertEqual(task_3.wsjf, 12.0)

    def test_inverse_internal_pressure(self):
        self.project_1.write({
            'business_value': 1,
            'time_criticality': 1,
            'risk_reduction': 1,
            'internal_pressure': 13,
            'job_size': 1,
        })
        self.project_2.write({
            'business_value': 1,
            'time_criticality': 1,
            'risk_reduction': 1,
            'internal_pressure': 5,
            'job_size': 1,
        })
        self.assertEqual(self.task_1.internal_pressure, 13.0)
        self.assertEqual(self.task_2.internal_pressure, 5.0)
