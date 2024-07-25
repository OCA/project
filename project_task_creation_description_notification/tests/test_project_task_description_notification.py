# Copyright 2024 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestProjectTaskDescriptionNotification(TransactionCase):

    # Use case : Prepare some data for current test case
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.description = "A test description"
        cls.project = cls.env["project.project"].create({"name": "Project Test"})
        cls.project_task = cls.env["project.task"].create(
            {
                "name": "Project Task Test",
                "description": cls.description,
                "project_id": cls.project.id,
            }
        )

    def test_project_task_description_notification(self):
        self.assertIn(self.description, self.project_task.message_ids.body)
