# Copyright 2021 Akretion (https://www.akretion.com).
# @author Kévin ROche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestDuplicatedTasksProcesses(TransactionCase):
    def setUp(self):
        super().setUp()

        self.project1 = self.env["project.project"].create({"name": "Clones project"})

        self.task1 = self.env["project.task"].create(
            {"name": "Clone 1", "project_id": self.project1.id}
        )
        self.task2 = self.env["project.task"].create(
            {"name": "Clone 2", "project_id": self.project1.id}
        )
        self.task3 = self.env["project.task"].create(
            {"name": "Clone 3", "project_id": self.project1.id}
        )
        self.subtask1 = self.env["project.task"].create(
            {
                "name": "Left side",
                "project_id": self.project1.id,
                "parent_id": self.task1.id,
            }
        )

        self.task1.duplicated_task_status_action()
        self.task1.task_duplicated_open_ids = [(4, self.task2.id)]

    def test_duplicate_stage(self):
        duplicated_stage = self.env.ref(
            "project_duplicated_task.project_stage_duplicated"
        )
        self.assertTrue(self.task1.stage_id, duplicated_stage)
        self.task1.duplicated_task_status_action()
        self.assertFalse(self.task1.stage_id, duplicated_stage)

    def test_close_duplicated_task(self):
        self.assertTrue(self.task1.is_duplicate)
        self.assertTrue(self.task2.id in self.task1.task_duplicated_open_ids.ids)
        self.task1._fill_open_duplicated_task()
        self.assertTrue(self.task1.id in self.task2.task_duplicated_closed_ids.ids)
        self.assertTrue(self.task2.have_duplicate)

    def test_close_duplicated_task_in_cascade(self):
        self.task1._fill_open_duplicated_task()
        self.task2.duplicated_task_status_action()
        self.task2.task_duplicated_open_ids = [(4, self.task3.id)]
        self.task2._fill_open_duplicated_task()
        self.assertTrue(self.task1.id in self.task3.task_duplicated_closed_ids.ids)
        self.assertTrue(self.task3.id in self.task1.task_duplicated_open_ids.ids)

    def test_reopen_duplicated_task(self):
        self.task1.duplicated_task_status_action()
        self.assertFalse(self.task1.is_duplicate)
        self.assertEqual(len(self.task1.task_duplicated_open_ids), 0)
        self.task1._fill_open_duplicated_task()
        self.assertFalse(self.task2.have_duplicate)
        self.assertEqual(len(self.task2.task_duplicated_closed_ids), 0)

    def test_duplicate_task_with_subtasks(self):
        self.assertTrue(self.subtask1.is_duplicate)
        self.assertTrue(
            self.subtask1.stage_id,
            self.env.ref("project_duplicated_task.project_stage_duplicated"),
        )
        self.subtask1._fill_open_duplicated_task()
        self.assertTrue(self.subtask1.id in self.task2.task_duplicated_closed_ids.ids)
        self.assertTrue(self.task2.id in self.subtask1.task_duplicated_open_ids.ids)

    # def test_warning_open_duplicated_task_required(self):
    #     self.task3.duplicated_task_status_action()
