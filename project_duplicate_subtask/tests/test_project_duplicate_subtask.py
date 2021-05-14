# Copyright (C) 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestProjectDuplicateSubtask(TransactionCase):
    def setUp(self):
        super().setUp()

        self.project1 = self.env["project.project"].create({"name": "Project 1"})
        self.task1 = self.env["project.task"].create(
            {"name": "name1", "project_id": self.project1.id}
        )
        self.subtask1 = self.env["project.task"].create(
            {"name": "2", "project_id": self.project1.id, "parent_id": self.task1.id}
        )
        self.subtask2 = self.env["project.task"].create(
            {"name": "3", "project_id": self.project1.id, "parent_id": self.task1.id}
        )

    def test_check_subtasks(self):
        self.task1.action_duplicate_subtasks()

        new_task = self.env["project.task"].search(
            [("name", "ilike", self.task1.name), ("name", "ilike", "copy")]
        )
        self.assertEqual(
            len(new_task.child_ids), 2, "Two subtasks should have been created"
        )
