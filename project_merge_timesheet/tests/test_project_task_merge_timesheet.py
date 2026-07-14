# Copyright 2026 Cyril VINH-TUNG (INVITU) <cyril@invitu.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.project.tests.test_project_base import TestProjectCommon


@tagged("-at_install", "post_install")
class TestProjectMergeTimesheet(TestProjectCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Test Employee", "employee_type": "freelance"}
        )

    def test_merge_moves_timesheets(self):
        """timesheet lines of the merged task are moved to the destination
        task, and their project follows automatically"""
        task_A = self.env["project.task"].create(
            {"name": "Task A", "project_id": self.project_goats.id}
        )
        task_B = self.env["project.task"].create(
            {"name": "Task B", "project_id": self.project_goats.id}
        )
        timesheet_B = self.env["account.analytic.line"].create(
            {
                "name": "Work on task B",
                "project_id": task_B.project_id.id,
                "task_id": task_B.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.5,
            }
        )

        task_merge = (
            self.env["project.task.merge"]
            .with_context(active_ids=[task_A.id, task_B.id])
            .create({})
        )
        task_merge.merge_tasks()

        self.assertEqual(timesheet_B.task_id, task_merge.dst_task_id)
        self.assertEqual(timesheet_B.project_id, task_merge.dst_task_id.project_id)

    def test_merge_without_timesheets_on_private_task(self):
        """merging tasks with no timesheets into a private (project-less)
        task must not raise, even though such tasks cannot receive
        timesheets"""
        task_private_A = self.env["project.task"].create({"name": "Private A"})
        task_private_B = self.env["project.task"].create({"name": "Private B"})

        task_merge = (
            self.env["project.task.merge"]
            .with_context(active_ids=[task_private_A.id, task_private_B.id])
            .create({})
        )
        task_merge.merge_tasks()

        self.assertFalse(task_merge.dst_task_id.project_id)
