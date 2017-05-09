# -*- coding: utf-8 -*-
# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

from odoo.tests import common
from odoo import fields
from datetime import timedelta, datetime


class TestProjectIssueTimesheetTimeControl(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProjectIssueTimesheetTimeControl, cls).setUpClass()
        cls.project = cls.env['project.project'].create(
            {'name': 'Test project'})
        cls.analytic_account = cls.project.analytic_account_id
        cls.issue = cls.env['project.issue'].create({
            'name': 'Test issue',
            'project_id': cls.project.id,
            'analytic_account_id': cls.analytic_account.id,
        })
        task_type_obj = cls.env['project.task.type']
        cls.stage_open = task_type_obj.create({
            'name': 'New',
            'closed': False,
            'project_ids': [(6, 0, cls.project.ids)],
        })
        cls.stage_close = task_type_obj.create({
            'name': 'Done',
            'closed': True,
            'project_ids': [(6, 0, cls.project.ids)],
        })
        date_time = fields.Datetime.to_string(
            datetime.now() - timedelta(hours=1))
        cls.line = cls.env['account.analytic.line'].create({
            'date_time': date_time,
            'issue_id': cls.issue.id,
            'account_id': cls.analytic_account.id,
            'name': 'Test line',
        })

    def test_onchange_project_id(self):
        record = self.env['account.analytic.line'].new()
        record.project_id = self.project.id
        action = (
            record.onchange_project_id_project_issue_timesheet_time_control()
        )
        self.assertTrue(action['domain']['issue_id'])

    def test_onchange_issue_id(self):
        record = self.env['account.analytic.line'].new()
        record.issue_id = self.issue.id
        record.onchange_issue_id_project_issue_timesheet_time_control()
        self.assertEqual(record.project_id, self.project)

    def test_open_close_issue(self):
        self.line.button_close_issue()
        self.assertEqual(self.line.issue_id.stage_id, self.stage_close)
        self.line.button_open_issue()
        self.assertEqual(self.line.issue_id.stage_id, self.stage_open)
