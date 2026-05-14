from odoo import Command
from odoo.tests.common import TransactionCase


class TestProjectTaskDefaultUser(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        group_user = cls.env.ref("base.group_user")
        group_project = cls.env.ref("project.group_project_user")
        cls.user1 = env["res.users"].create(
            {
                "name": "User 1",
                "login": "user1",
                "email": "user1@example.com",
                "group_ids": [
                    Command.link(group_user.id),
                    Command.link(group_project.id),
                ],
            }
        )
        cls.user2 = env["res.users"].create(
            {
                "name": "User 2",
                "login": "user2",
                "email": "user2@example.com",
                "group_ids": [
                    Command.link(group_user.id),
                    Command.link(group_project.id),
                ],
            }
        )
        cls.project_with_default = env["project.project"].create(
            {
                "name": "Project with Default",
                "default_user_ids": [Command.set([cls.user1.id])],
            }
        )
        cls.project_without_default = env["project.project"].create(
            {
                "name": "Project without Default",
            }
        )
        cls.stage_with_default = env["project.task.type"].create(
            {
                "name": "Stage with Default",
                "default_user_ids": [Command.link(cls.user2.id)],
                "project_ids": [Command.link(cls.project_with_default.id)],
                "stage_task_assignment_mode": "replace",
            }
        )

        cls.stage_without_default = env["project.task.type"].create(
            {
                "name": "Stage without Default",
                "project_ids": [Command.link(cls.project_with_default.id)],
                "stage_task_assignment_mode": "replace",
            }
        )

    def test_create_task_stage_default(self):
        task = self.env["project.task"].create(
            {
                "name": "Task Stage Default",
                "project_id": self.project_with_default.id,
                "stage_id": self.stage_with_default.id,
            }
        )
        self.assertEqual(task.user_ids.ids, [self.user2.id])

    def test_create_task_project_default(self):
        task = self.env["project.task"].create(
            {
                "name": "Task Project Default",
                "project_id": self.project_with_default.id,
                "stage_id": self.stage_without_default.id,
            }
        )
        self.assertEqual(task.user_ids.ids, [self.user1.id])

    def test_create_task_no_default(self):
        task = self.env["project.task"].create(
            {
                "name": "Task No Default",
                "project_id": self.project_without_default.id,
                "stage_id": self.stage_without_default.id,
            }
        )
        self.assertFalse(set(task.user_ids.ids) & {self.user1.id, self.user2.id})

    def test_stage_change_with_default(self):
        task = self.env["project.task"].create(
            {
                "name": "Task Change Stage",
                "project_id": self.project_with_default.id,
                "stage_id": self.stage_without_default.id,
            }
        )
        task.stage_id = self.stage_with_default
        self.assertEqual(task.user_ids.ids, [self.user2.id])

    def test_stage_change_no_default(self):
        task = self.env["project.task"].create(
            {
                "name": "Task Change Stage",
                "project_id": self.project_with_default.id,
                "stage_id": self.stage_with_default.id,
            }
        )
        task.stage_id = self.stage_without_default
        self.assertEqual(task.user_ids.ids, [self.user1.id])

    def test_stage_merge_with_existing_user(self):
        self.stage_with_default.write(
            {
                "stage_task_assignment_mode": "merge",
            }
        )
        task = self.env["project.task"].create(
            {
                "name": "Merge With Existing",
                "user_ids": [Command.link(self.user1.id)],
                "project_id": self.project_without_default.id,
                "stage_id": self.stage_with_default.id,
            }
        )
        self.assertEqual(set(task.user_ids.ids), {self.user1.id, self.user2.id})

    def test_stage_merge_without_existing_user(self):
        self.stage_with_default.write(
            {
                "stage_task_assignment_mode": "merge",
            }
        )
        task = self.env["project.task"].create(
            {
                "name": "Empty Merge",
                "user_ids": False,
                "project_id": self.project_without_default.id,
                "stage_id": self.stage_with_default.id,
            }
        )
        self.assertEqual(set(task.user_ids.ids), {self.user2.id})
