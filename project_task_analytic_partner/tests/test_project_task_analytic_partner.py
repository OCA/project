# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestTaskAnalyticPartner(TransactionCase):
    def setUp(self):
        super(TestTaskAnalyticPartner, self).setUp()
        self.project = self.env.ref('project.project_project_1')
        self.partner1 = self.env.ref('base.res_partner_2')
        self.partner2 = self.env.ref('base.res_partner_12')
        self.task = self.env['project.task'].create(
            {'name': 'Task Test 1',
             'project_id': self.project.id})
        self.factor = self.env.ref(
            'hr_timesheet_invoice.timesheet_invoice_factor1')

    def test_task_analytic_partner(self):
        work_line = self.env['project.task.work'].create({
            'task_id': self.task.id,
            'name': 'Work test battery',
            'hours': 1,
            'to_invoice': self.factor.id,
            'other_partner_id': self.partner1.id,
            'user_id': self.uid,
        })
        self.assertEqual(work_line.hr_analytic_timesheet_id.other_partner_id,
                         self.partner1)
        self.assertEqual(work_line.hr_analytic_timesheet_id.to_invoice,
                         self.factor)
        work_line.other_partner_id = self.partner2
        self.assertEqual(work_line.hr_analytic_timesheet_id.other_partner_id,
                         self.partner2)
        work_line.to_invoice = False
        self.assertFalse(work_line.hr_analytic_timesheet_id.to_invoice)
