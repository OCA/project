# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form, TransactionCase, new_test_user


class TestProjectTaskAssignToMe(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user = new_test_user(
            cls.env, login="test-assign-to-me", groups="project.group_project_user"
        )
        cls.other_user = new_test_user(
            cls.env, login="test-assign-other", groups="project.group_project_user"
        )
        cls.project = cls.env["project.project"].create({"name": "Test project"})
        cls.task = cls.env["project.task"].create(
            {"name": "Test task", "project_id": cls.project.id, "user_ids": False}
        )

    def test_assign_to_me_unassigned_task(self):
        self.task.with_user(self.user).action_assign_to_me()
        self.assertEqual(self.task.user_ids, self.user)

    def test_assign_to_me_keeps_other_assignees(self):
        with Form(self.task) as task_form:
            task_form.user_ids.add(self.other_user)
        self.task.with_user(self.user).action_assign_to_me()
        self.assertEqual(self.task.user_ids, self.user | self.other_user)
