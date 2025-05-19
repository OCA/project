from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class ProjectMilestoneStatusCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.timesheet_line_model = cls.env["account.analytic.line"]
        cls.project1 = cls.env["project.project"].create({"name": "Project 1"})
        cls.milestone1 = cls.env["project.milestone"].create(
            {"name": "Milestone 1", "project_id": cls.project1.id}
        )
        cls.user = new_test_user(
            cls.env, login="test-user", groups="hr_timesheet.group_hr_timesheet_user"
        )
        cls.employee_1 = cls.env["hr.employee"].create(
            {
                "name": "Test employee 1",
                "user_id": cls.user.id,
            }
        )
        cls.task1 = cls.env["project.task"].create(
            {
                "name": "name1",
                "project_id": cls.project1.id,
                "milestone_id": cls.milestone1.id,
                "allocated_hours": 5.0,
            }
        )
        cls.task2 = cls.env["project.task"].create(
            {
                "name": "name2",
                "project_id": cls.project1.id,
                "milestone_id": cls.milestone1.id,
                "allocated_hours": 5.0,
            }
        )
