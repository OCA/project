# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo.addons.project.tests.test_project_base import TestProjectCommon


class TestProjectTaskAncestor(TestProjectCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ancestor_task = (
            cls.env["project.task"]
            .with_context(mail_create_nolog=True)
            .create(
                {
                    "name": "Test Project Task Ancestor",
                    "user_ids": cls.user_projectmanager,
                    "project_id": cls.project_pigs.id,
                }
            )
        )
        cls.task_3 = (
            cls.env["project.task"]
            .with_context(mail_create_nolog=True)
            .create(
                {
                    "name": "Test Task",
                    "user_ids": cls.user_projectmanager,
                    "project_id": cls.project_pigs.id,
                }
            )
        )

    def test_ancestor_task(self):
        self.task_1.parent_id = self.ancestor_task
        self.task_2.parent_id = self.task_1
        self.task_3.parent_id = self.task_2
        self.assertEqual(self.ancestor_task, self.task_1.ancestor_id)
        self.assertEqual(self.ancestor_task, self.task_2.ancestor_id)
        self.assertEqual(self.ancestor_task, self.task_3.ancestor_id)

    def test_ancestor_task_reports(self):
        self.task_1.parent_id = self.ancestor_task
        self.task_2.parent_id = self.task_1
        employee = self.env["hr.employee"].create(
            {"name": "Test Employee", "user_id": self.user_projectmanager.id}
        )
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "project_id": self.project_pigs.id,
                "task_id": self.task_2.id,
                "employee_id": employee.id,
                "unit_amount": 2.0,
            }
        )
        self.assertEqual(timesheet.ancestor_task_id, self.ancestor_task)
        self.env.flush_all()
        # Task analysis report
        task_report = self.env["report.project.task.user"].search(
            [("task_id", "=", self.task_2.id)]
        )
        self.assertEqual(task_report.ancestor_id, self.ancestor_task)
        groups = dict(
            self.env["report.project.task.user"].read_group(
                [("project_id", "=", self.project_pigs.id)],
                ["ancestor_id"],
                ["__count"],
            )
        )
        self.assertEqual(groups[self.ancestor_task.id], 2)
        # Timesheet analysis report
        timesheet_report = self.env["timesheets.analysis.report"].search(
            [("id", "=", timesheet.id)]
        )
        self.assertEqual(timesheet_report.ancestor_task_id, self.ancestor_task)
        self.assertEqual(
            self.env["timesheets.analysis.report"].search_count(
                [("ancestor_task_id", "=", self.ancestor_task.id)]
            ),
            1,
        )
