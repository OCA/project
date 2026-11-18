# Copyright 2026 Forgeflow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestProjectTaskCodeByProject(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_task_model = cls.env["project.task"]
        cls.global_sequence = cls.env.ref("project_task_code.sequence_task")
        cls.project_with_seq = cls.env["project.project"].create(
            {"name": "Project With Sequence"}
        )
        cls.project_without_seq = cls.env["project.project"].create(
            {"name": "Project Without Sequence"}
        )
        cls.project_sequence = cls.env["ir.sequence"].create(
            {
                "name": "Test Project Task Sequence",
                "code": "project.task.test",
                "padding": 4,
                "prefix": "PWS-",
            }
        )
        cls.project_with_seq.task_sequence_id = cls.project_sequence

    def test_task_with_project_sequence_flow(self):
        project_next = self.project_sequence.number_next_actual
        project_expected = self.project_sequence.get_next_char(project_next)
        global_next_before = self.global_sequence.number_next_actual
        task = self.project_task_model.create(
            {
                "name": "Task with project sequence",
                "project_id": self.project_with_seq.id,
            }
        )
        self.assertEqual(task.code, project_expected)
        self.assertTrue(task.code.startswith("PWS-"))
        self.assertRegex(task.display_name, f"\\[{project_expected}\\]")
        self.assertEqual(self.global_sequence.number_next_actual, global_next_before)

    def test_task_fallback_to_global_sequence_flow(self):
        global_next = self.global_sequence.number_next_actual
        global_expected = self.global_sequence.get_next_char(global_next)
        task_no_project = self.project_task_model.create(
            {"name": "Task without project"}
        )
        self.assertEqual(task_no_project.code, global_expected)
