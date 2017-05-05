# -*- coding: utf-8 -*-
# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

from odoo.tests import common
from odoo import fields
from datetime import timedelta, datetime


class TestProjectTimesheetTimeControl(common.TransactionCase):
    def setUp(self):
        super(TestProjectTimesheetTimeControl, self).setUp()
        self.project = self.env['project.project'].create(
            {'name': 'Test project'})
        self.analytic_account = self.project.analytic_account_id
        self.task = self.env['project.task'].create({
            'name': 'Test task',
            'project_id': self.project.id,
        })
        task_type_obj = self.env['project.task.type']
        self.stage_open = task_type_obj.create({
            'name': 'New',
            'closed': False,
            'project_ids': [(6, 0, self.project.ids)],
        })
        self.stage_close = task_type_obj.create({
            'name': 'Done',
            'closed': True,
            'project_ids': [(6, 0, self.project.ids)],
        })
        date_time = fields.Datetime.to_string(
            datetime.now() - timedelta(hours=1))
        self.line = self.env['account.analytic.line'].create({
            'date_time': date_time,
            'task_id': self.task.id,
            'account_id': self.analytic_account.id,
            'name': 'Test line',
        })

    def test_onchange_project_id(self):
        record = self.env['account.analytic.line'].new()
        record.project_id = self.project.id
        action = record.onchange_project_id()
        self.assertTrue(action['domain']['task_id'])

    def test_onchange_task_id(self):
        record = self.env['account.analytic.line'].new()
        record.task_id = self.task.id
        record.onchange_task_id()
        self.assertEqual(record.project_id, self.project)

    def test_create_write_analytic_line(self):
        line = self.env['account.analytic.line'].create({
            'date_time': fields.Datetime.now(),
            'account_id': self.analytic_account.id,
            'name': 'Test line',
        })
        self.assertEqual(line.date, fields.Date.today())
        line.date_time = '2016-03-23 18:27:00'
        self.assertEqual(line.date, '2016-03-23')

    def test_button_end_work(self):
        self.line.button_end_work()
        self.assertTrue(self.line.unit_amount)

    def test_open_close_task(self):
        self.line.button_close_task()
        self.assertEqual(self.line.task_id.stage_id, self.stage_close)
        self.line.button_open_task()
        self.assertEqual(self.line.task_id.stage_id, self.stage_open)
