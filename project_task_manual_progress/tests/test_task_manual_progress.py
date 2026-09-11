# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestTaskManualProgress(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create({"name": "Test Project"})

    def test_manual_progress_constraint_ok(self):
        task = self.env["project.task"].create(
            {
                "name": "Task OK",
                "project_id": self.project.id,
                "manual_progress": 50,
            }
        )
        self.assertEqual(task.manual_progress, 50)

    def test_manual_progress_constraint_ko(self):
        with self.assertRaises(ValidationError):
            self.env["project.task"].create(
                {
                    "name": "Task KO",
                    "project_id": self.project.id,
                    "manual_progress": 150,
                }
            )

    def test_project_manual_progress_compute(self):
        self.env["project.task"].create(
            {
                "name": "Task 1",
                "project_id": self.project.id,
                "manual_progress": 20,
            }
        )
        self.env["project.task"].create(
            {
                "name": "Task 2",
                "project_id": self.project.id,
                "manual_progress": 40,
            }
        )
        self.assertEqual(self.project.manual_progress, 30)

    def test_project_manual_progress_no_tasks(self):
        empty_project = self.env["project.project"].create({"name": "Empty Project"})
        self.assertEqual(empty_project.manual_progress, 0)
