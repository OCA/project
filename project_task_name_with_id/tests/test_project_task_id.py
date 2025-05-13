# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo.tests.common import TransactionCase


class TestProjectTaskID(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProjectTask = cls.env["project.task"]
        cls.project_task = cls.ProjectTask.create(
            {
                "name": "Test task",
            }
        )

    def test_name_search(self):
        # Test searching by name
        tasks = self.ProjectTask.name_search("Test task")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0][0], self.project_task.id)

        # Test searching by ID
        tasks = self.ProjectTask.name_search(str(self.project_task.id))
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0][0], self.project_task.id)

    def test_display_name(self):
        display_name = self.project_task.display_name
        task_id = self.project_task.id
        # Checking for the task ID and "Test task" anywhere in the string
        pattern = re.compile(rf"\[{task_id}\].*Test task")
        self.assertTrue(pattern.search(display_name))
