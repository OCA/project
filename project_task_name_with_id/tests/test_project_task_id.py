# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo.tests.common import TransactionCase


class TestProjectTaskID(TransactionCase):
    def setUp(self):
        super(TestProjectTaskID, self).setUp()
        self.ProjectTask = self.env["project.task"]
        self.project_task = self.ProjectTask.create(
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

    def test_name_get(self):
        # Test the new name_get method
        name_get = self.project_task.name_get()[0]
        self.assertEqual(name_get[0], self.project_task.id)
        task_id = self.project_task.id
        # Checking for the task ID and "Test task" anywhere in the string
        pattern = re.compile(rf"\[{task_id}\].*Test task")
        self.assertTrue(pattern.search(name_get[1]))
