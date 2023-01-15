from odoo.tests import common
from odoo.addons.hr_timesheet.tests.test_timesheet import TestCommonTimesheet
#from odoo.addons.project_timesheet_time_control.tests import TestProjectTimesheetTimeControl


class TestProjectTimesheetTimetype(TestCommonTimesheet):
    
    def setUp(self):
        super(TestProjectTimesheetTimetype, self).setUp()
        # add stages to project_customer
        print(f"**** {self.project_customer.id}. {self.project_customer.name}")
        self.project_task_type_1 = self.env['project.task.type'].create({
            'name': "Stage 1",
            'project_ids': [(6,0,[self.project_customer.id])]
        })
        self.project_task_type_2 = self.env['project.task.type'].create({
            'name': "Stage 2",
            'project_ids': [(6,0,[self.project_customer.id])]
        })
        
        # set task1 in stage 1
        self.task1.stage_id = self.project_task_type_1.id

        self.timetype1 = self.env['project.time.type'].create({
            'name': "timetype1"
        })
        self.timetype2 = self.env['project.time.type'].create({
            'name': "timetype2"
        })
        self.timetype3 = self.env['project.time.type'].create({
            'name': "timetype3"
        })

        # Default rules
        self.timetype_rule_1 = self.env['project.time.type.rule'].create({
            'project_type_id': self.project_task_type_1.id,
            'time_type_id': self.timetype1.id
        })
        
    def test_rules(self):
        """Rule precedence: employee, department, project, project_type"""

        Timesheet = self.env['account.analytic.line']
        timesheet0 = Timesheet.with_user(self.user_manager).create({
            'project_id': self.project_customer.id,
            'task_id': self.task2.id,
            'name': 'timesheet without type',
            'unit_amount': 1,
        })
        self.assertFalse(timesheet0.time_type_id)

        timesheet1 = Timesheet.with_user(self.user_manager).create({
            'project_id': self.project_customer.id,
            'task_id': self.task1.id,
            'name': 'my first timesheet',
            'unit_amount': 4,
        })
        self.assertEqual(timesheet1.time_type_id, self.timetype1)
        # Project rule has precedence
        self.timetype_rule_2 = self.env['project.time.type.rule'].create({
            'project_id': self.project_customer.id,
            'time_type_id': self.timetype2.id
        })
        timesheet2 = Timesheet.with_user(self.user_manager).create({
            'project_id': self.project_customer.id,
            'task_id': self.task1.id,
            'name': 'my Second timesheet',
            'unit_amount': 6,
        })
        self.assertEqual(timesheet2.time_type_id, self.timetype2)
        
        # TODO: employee rule's test
        
