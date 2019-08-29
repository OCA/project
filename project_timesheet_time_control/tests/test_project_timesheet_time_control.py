# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

from odoo.tests import common
from odoo import fields
from datetime import timedelta, date, datetime


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
        self.line = self.env['account.analytic.line'].create({
            'date_time': datetime.now() - timedelta(hours=1),
            'task_id': self.task.id,
            'account_id': self.analytic_account.id,
            'name': 'Test line',
        })

    def test_create_write_analytic_line(self):
        line = self.env['account.analytic.line'].create({
            'date_time': fields.Datetime.now(),
            'account_id': self.analytic_account.id,
            'name': 'Test line',
        })
        self.assertEqual(line.date, fields.Date.today())
        line.date_time = '2016-03-23 18:27:00'
        self.assertEqual(line.date, date(2016, 3, 23))

    def test_button_end_work(self):
        self.line.button_end_work()
        self.assertTrue(self.line.unit_amount)
