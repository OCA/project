from odoo.addons.hr_timesheet.tests.test_timesheet import TestCommonTimesheet

# from odoo.addons.project_timesheet_time_control.tests import TestProjectTimesheetTimeControl

# ./opts.sh tst o14test project_timesheet_time_control_type


class TestProjectTimesheetTimetype(TestCommonTimesheet):
    def setUp(self):
        super(TestProjectTimesheetTimetype, self).setUp()
        # add stages to project_customer
        self.project_task_type_1 = self.env["project.task.type"].create(
            {"name": "Stage 1", "project_ids": [(6, 0, [self.project_customer.id])]}
        )
        self.project_task_type_2 = self.env["project.task.type"].create(
            {"name": "Stage 2", "project_ids": [(6, 0, [self.project_customer.id])]}
        )

        # set task1 in stage 1
        self.task1.stage_id = self.project_task_type_1.id

        self.timetype1 = self.env["project.time.type"].create({"name": "timetype1"})
        self.timetype2 = self.env["project.time.type"].create({"name": "timetype2"})
        self.timetype3 = self.env["project.time.type"].create({"name": "timetype3"})
        self.timetype4 = self.env["project.time.type"].create({"name": "timetype4"})

        self.department1 = self.env["hr.department"].create({"name": "Department1"})
        self.empl_employee.department_id = self.department1

        # Default rules
        self.timetype_rule_1 = self.env["project.time.type.rule"].create(
            {
                "project_type_id": self.project_task_type_1.id,
                "time_type_id": self.timetype1.id,
            }
        )

    def test_rules_precedence(self):
        """Rule precedence: employee, department, project, project_type"""

        Timesheet = self.env["account.analytic.line"]
        timesheet0 = Timesheet.with_user(self.user_manager).create(
            {
                "project_id": self.project_customer.id,
                "task_id": self.task2.id,
                "name": "timesheet without type",
                "unit_amount": 1,
            }
        )
        self.assertFalse(timesheet0.time_type_id)

        timesheet1 = Timesheet.with_user(self.user_manager).create(
            {
                "project_id": self.project_customer.id,
                "task_id": self.task1.id,
                "name": "my first timesheet",
                "unit_amount": 11,
            }
        )
        self.assertEqual(timesheet1.time_type_id, self.timetype1)

        self.timetype_rule_2 = self.env["project.time.type.rule"].create(
            {"project_id": self.project_customer.id, "time_type_id": self.timetype2.id}
        )
        # Project rule has precedence
        timesheet2 = Timesheet.with_user(self.user_manager).create(
            {
                "project_id": self.project_customer.id,
                "task_id": self.task1.id,
                "name": "my Second timesheet",
                "unit_amount": 12,
            }
        )
        self.assertEqual(timesheet2.time_type_id, self.timetype2)

        # department has precedence
        self.timetype_rule_3 = self.env["project.time.type.rule"].create(
            {"department_id": self.department1.id, "time_type_id": self.timetype3.id}
        )
        timesheet3 = Timesheet.with_user(self.user_employee).create(
            {
                "project_id": self.project_customer.id,
                "task_id": self.task1.id,
                "name": "my timesheet as user_employee.department_id",
                "unit_amount": 13,
            }
        )
        self.assertEqual(timesheet3.time_type_id, self.timetype3)

        # user has precedence
        self.timetype_rule_4 = self.env["project.time.type.rule"].create(
            {"employee_id": self.empl_employee.id, "time_type_id": self.timetype4.id}
        )
        timesheet4 = Timesheet.with_user(self.user_employee).create(
            {
                "project_id": self.project_customer.id,
                "task_id": self.task1.id,
                "name": "my timesheet as user_employee",
                "unit_amount": 14,
            }
        )
        self.assertEqual(timesheet4.time_type_id, self.timetype4)

    def test_rules_default_user(self):
        Timesheet = self.env["account.analytic.line"]
        # Default employee
        timesheet5 = Timesheet.with_context(
            default_employee_id=self.empl_employee2.id
        ).create(
            {
                "project_id": self.project_customer.id,
                "task_id": self.task1.id,
                "name": "my timesheet as default user_employee2",
                "unit_amount": 15,
            }
        )
        # Stage time type? Project precedence?
        self.assertEqual(timesheet5.time_type_id, self.timetype1)
