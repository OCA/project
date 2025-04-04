from odoo.tests import tagged

from odoo.addons.project.tests.test_project_base import TestProjectCommon


@tagged("post_install", "-at_install")
class TestTaskRelated(TestProjectCommon):
    def test_write_relation(self):
        self.task_1.write({"related_task_ids": [(4, self.task_2.id)]})
        self.assertIn(
            self.task_2.id, self.task_1.related_task_ids.ids, "Forward relation Failed"
        )
        self.assertIn(
            self.task_1.id, self.task_2.related_task_ids.ids, "Reverse relation Failed"
        )

    def test_create_with_relation(self):
        self.task_custom = (
            self.env["project.task"]
            .with_context(mail_create_nolog=True)
            .create(
                {
                    "name": "Pigs ManagerTask 2",
                    "user_ids": self.user_projectmanager,
                    "project_id": self.project_pigs.id,
                    "related_task_ids": [(4, self.task_1.id)],
                }
            )
        )
        self.assertIn(
            self.task_1.id,
            self.task_custom.related_task_ids.ids,
            "Forward relation Failed",
        )
        self.assertIn(
            self.task_custom.id,
            self.task_1.related_task_ids.ids,
            "Reverse relation Failed",
        )

    def test_remove_relation(self):
        self.task_3 = (
            self.env["project.task"]
            .with_context(mail_create_nolog=True)
            .create(
                {
                    "name": "Test task 3",
                    "user_ids": self.user_projectmanager,
                    "project_id": self.project_pigs.id,
                }
            )
        )

        self.task_1.write({"related_task_ids": [(4, self.task_2.id)]})
        self.task_1.write({"related_task_ids": [(4, self.task_3.id)]})

        self.task_1.write({"related_task_ids": [(3, self.task_2.id)]})
        self.assertNotIn(
            self.task_2.id, self.task_1.related_task_ids.ids, "Delete relation failed"
        )
        self.assertIn(
            self.task_3.id,
            self.task_1.related_task_ids.ids,
            "Deleted unrelated pairing",
        )
