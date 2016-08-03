# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestProjectTaskCreateAlerts(TransactionCase):

    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestProjectTaskCreateAlerts, self).setUp()
        self.project = self.env['project.project'].create({
            'name': 'Project Test'
        })
        self.partner1 = self.env['res.partner'].create({
            'name': 'Partner Test1',
            'date': '2016-07-24',
        })
        self.partner2 = self.env['res.partner'].create({
            'name': 'Partner Test1',
            'date': '2016-07-29',
        })
        self.date_field_id = self.env.ref('base.field_res_partner_date').id
        self.task_alert1 = self.env['project.task.alert'].create({
            'name': 'Task Alert Test1',
            'project_id': self.project.id,
            'days_delta': 3,
            'task_description': 'Description of Task Alert1',
            'date_field_id': self.date_field_id,
        })
        self.task_alert2 = self.env['project.task.alert'].create({
            'name': 'Task Alert Test2',
            'project_id': self.project.id,
            'days_delta': 8,
            'task_description': 'Description of Task Alert2',
            'date_field_id': self.date_field_id,
        })

    def test_create_alerts(self):
        self.task_alert1.create_task_alerts()
        task = self.env['project.task'].search([
            ('name', '=', 'Task Alert Test1')])
        self.assertEqual(len(task), 1)

    def test_run_alerts(self):
        self.env['project.task.alert'].run_task_alerts()
        task = self.env['project.task'].search([
            ('name', '=', 'Task Alert Test2')])
        self.assertEqual(len(task), 1)
