# -*- coding: utf-8 -*-
# © 2013 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
import datetime

dt_combine = datetime.datetime.combine
dt_delta = datetime.timedelta

thursday = datetime.date(2015, 4, 9)
friday = thursday + dt_delta(days=1)
monday = friday + dt_delta(days=3)

thursday_8 = dt_combine(thursday, datetime.time(8))
thursday_10 = dt_combine(thursday, datetime.time(10))
thursday_15 = dt_combine(thursday, datetime.time(15))
thursday_17 = dt_combine(thursday, datetime.time(17))
thursday_19 = dt_combine(thursday, datetime.time(19))

friday_5 = dt_combine(friday, datetime.time(5))
friday_9 = dt_combine(friday, datetime.time(9))
friday_10 = dt_combine(friday, datetime.time(10))
friday_11 = dt_combine(friday, datetime.time(11))
friday_13 = dt_combine(friday, datetime.time(13))

monday_10 = dt_combine(monday, datetime.time(10))


class TestSla(TransactionCase):

    def setUp(self):
        super(TestSla, self).setUp()
        self.model = self.env['project.sla.control'].sudo()
        if 'tz' not in self.model.env.context:
            self.model = self.model.with_context(tz='UTC')
        # Tests using 8-12 13-18 demo data calendar
        self.calendar_id = self.env.ref('resource.timesheet_group1').id

    def test_10(self):
        model = self.model
        calendar_id = self.calendar_id

        def compute(date, hours):
            return model._compute_sla_date(
                calendar_id, self.env.user.id, date, hours)

        self.assertEquals(compute(thursday_8, 2), thursday_10)

        # 1 hour time for a lunch break
        self.assertEquals(compute(thursday_10, 4), thursday_15)

        # working day ands in 18, so 17 + 2 hours must be friday 10
        self.assertEquals(compute(thursday_17, 2), friday_10)

        # when start_date is after end of working day
        # 3 hours count from 08:00 to 11:00
        self.assertEquals(compute(thursday_19, 3), friday_11)

        # when start_Date is before start of working day
        self.assertEquals(compute(friday_5, 3), friday_11)

        # end date should be moved correctly on next day
        self.assertEquals(compute(thursday_10, 10), friday_13)

        # correctly process weekends
        self.assertEquals(compute(thursday_15, 2 + 8 + 2), monday_10)

    def test_sla_on_issue(self):
        project = self.env.ref('project.project_project_1')
        # ----- Create an issue in the project
        issue = self.env['project.issue'].create({
            'name': 'Error on project SLA',
            'project_id': project.id,
            })
        # ----- Based on SLA rules, this issue must have 1 control line
        self.assertEquals(len(issue.sla_control_ids), 1)
        # ----- Add a rule to Analytic account
        project.analytic_account_id.sla_ids = [
            (4, self.env.ref('project_sla.sla_response').id)]
        # ----- Reapply rules to issue from analytic account
        project.analytic_account_id.reapply_sla()
        # ----- Based on SLA rules, this issue must have 2 control lines
        self.assertEquals(len(issue.sla_control_ids), 2)

    def test_sla_on_task(self):
        project = self.env.ref('project.project_project_1')
        # ----- Create an issue in the project
        task = self.env['project.task'].create({
            'name': 'Test for project SLA addon',
            'project_id': project.id,
            })
        # ----- Analytic account hasn't rules for task
        self.assertEquals(len(task.sla_control_ids), 0)
        # ----- Add a rule to Analytic account
        project.analytic_account_id.sla_ids = [
            (4, self.env.ref('project_sla.sla_task_response').id)]
        # ----- Reapply rules to issue from analytic account
        project.analytic_account_id.reapply_sla()
        # ----- Based on SLA rules, this issue must have 1 control line
        self.assertEquals(len(task.sla_control_ids), 1)
