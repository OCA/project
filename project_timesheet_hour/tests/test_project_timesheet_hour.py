# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProjectTimesheetHours(TransactionCase):

    def setUp(self):
        super(TestProjectTimesheetHours, self).setUp()
        self.AnalyticLineObj = self.env['account.analytic.line']
        self.ProjectObj = self.env['project.project']
        self.ProjectTaskObj = self.env['project.task']

        self.project = self.ProjectObj.create({
            'name': "Testing",
            'use_tasks': True,
            'allow_timesheets': True,
        })
        self.task = self.ProjectTaskObj.create({
            'name': "Testing",
            'project_id': self.project.id,
            'planned_hours': 40.0,
            'remaining_hours': 40.0,
        })

        self.service_product = self.env.ref('product.service_order_01')
        self.analytic_account_1 = self.env.ref('analytic.analytic_internal')

    def create_subtask(self, task, timesheet=True):
        return self.ProjectTaskObj.create({
            'name': "Test",
            'parent_id': task.id,
            'can_be_selected_on_timesheet': timesheet,
        })

    def create_analytic_line(self, task, hours):
        return self.AnalyticLineObj.create({
            'task_id': task.id,
            'unit_amount': hours,
            'name': "Test",
            'account_id': self.analytic_account_1.id,
        })

    def test_01_test_project_hours(self):
        task = self.task
        project = task.project_id
        self.assertEquals(project.planned_hours, 40)
        self.assertEquals(project.total_hours_spent, 0)

        self.create_analytic_line(task, 8)
        self.assertEquals(project.total_hours_spent, 8)
        self.assertEquals(project.progress, 20)

        subtask = self.create_subtask(task)
        self.assertEquals(task.subtask_count, 1)

        self.create_analytic_line(subtask, 2)
        self.assertEquals(project.total_hours_spent, 10)
        self.assertEquals(project.progress, 25)

        subtask2 = self.create_subtask(subtask)
        self.create_analytic_line(subtask2, 2)
        self.assertEquals(project.total_hours_spent, 12)
        self.assertEquals(project.progress, 30)
