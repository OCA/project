# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import fields


class TestProjectTimesheetAnalyticPartner(common.TransactionCase):

    def setUp(self):
        super(TestProjectTimesheetAnalyticPartner, self).setUp()
        self.task = self.env.ref('project.project_task_1')
        self.task.partner_id = self.env.ref('base.res_partner_1')

    def test_other_partner_create_task_work(self):
        task_work = self.env['project.task.work'].create(
            {'task_id': self.task.id,
             'date': fields.Date.today(),
             'name': 'Test',
             'user_id': self.env.uid,
             'hours': 2.0})
        self.assertEqual(
            task_work.hr_analytic_timesheet_id.other_partner_id,
            self.task.partner_id)

    def test_other_partner_change_task_partner(self):
        partner_2 = self.env.ref('base.res_partner_2')
        self.task.partner_id = partner_2
        for task_work in self.task.work_ids:
            self.assertEqual(
                task_work.hr_analytic_timesheet_id.other_partner_id, partner_2)
