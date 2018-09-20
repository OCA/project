# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date, datetime, time
from odoo.tests.common import TransactionCase


class TestSchedulingCommon(TransactionCase):
    def setUp(self):
        super(TestSchedulingCommon, self).setUp()

        self.restricted_project = self.env['project.project'].browse(
            self.ref("project_task_employee.restricted_project"))

        employee_obj = self.env['hr.employee']
        # these are all employees of the self.restricted_project
        # Pieter Parker
        self.root_emp = employee_obj.browse(self.ref("hr.employee_root"))
        # Jimmy Kosikin
        self.jth_emp = employee_obj.browse(self.ref("hr.employee_jth"))

        # these are all tasks of the self.restricted_project
        self.task_2 = self.env['project.task'].browse(
            self.ref("project_task_employee.restricted_task_2"))
        self.task_3 = self.env['project.task'].browse(
            self.ref("project_task_employee.restricted_task_3"))
        self.task_7 = self.env['project.task'].browse(
            self.ref("project_task_employee.restricted_task_7"))
        self.task_1 = self.env['project.task'].browse(
            self.ref("project_task_employee.restricted_task_1"))
        # set task dependency
        self.task_1.dependency_task_ids = [(6, 0, [self.task_7.id])]

        # set date_start to be used as date_deadline of all tasks and
        # date_start of the wizard
        calendar = self.root_emp.resource_calendar_id
        date_start = calendar._get_next_work_day(date.today())
        date_start = datetime.combine(date_start, time())
        # date_start = fields.Datetime.to_string(date_start)

        self.restricted_project.task_ids.write({'date_deadline': date_start})

        wizard_obj = self.env['project.task.scheduling.wizard']
        self.wizard = wizard_obj.create({})
        self.wizard.write({
            'date_start': date_start,
            'cooling_ratio': '0.1',
            'task_option': 'customized_list',
            'task_ids': [[6, False, self.restricted_project.task_ids.ids]],
        })

        # set tz 'UTC'
        self.root_emp.resource_id.user_id.tz = 'UTC'
        self.env.user.tz = 'UTC'

        self.wizard.init_accum_inter()
