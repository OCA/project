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
