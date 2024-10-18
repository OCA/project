# Copyright Binhex 2024
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).
from odoo.tests.common import TransactionCase


class TestTaskProjectStatus(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestTaskProjectStatus, cls).setUpClass()
        cls.stage = cls.env["project.project.stage"].create(
            {
                "name": "Stage",
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": " Test Project",
                "stage_id": cls.stage.id,
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
            }
        )

    def test_project_status(self):
        self.assertEqual(self.task.project_status.id, self.stage.id)
        self.project.stage_id = self.env["project.project.stage"].create(
            {
                "name": "New Stage",
            }
        )
        self.assertEqual(self.task.project_status.id, self.project.stage_id.id)
