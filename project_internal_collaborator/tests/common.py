from odoo.tests.common import TransactionCase


class TestProjectCollaboratorCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.config_obj = cls.env["res.config.settings"].sudo()
        cls.config_parameter_obj = cls.env["ir.config_parameter"].sudo()
        cls.res_users_obj = cls.env["res.users"].with_context(no_reset_password=True)
        cls.project_task_type_obj = cls.env["project.task.type"]
        cls.mail_activity_type_obj = cls.env["mail.activity.type"]
        cls.project_project_obj = cls.env["project.project"]
        cls.project_task_obj = cls.env["project.task"]

        cls.stage_a = cls.project_task_type_obj.create({"name": "a"})
        cls.stage_b = cls.project_task_type_obj.create({"name": "b"})

        project_user_group = cls.env.ref("project.group_project_user")
        project_manager_group = cls.env.ref("project.group_project_manager")

        cls.demo_user = cls.res_users_obj.create(
            {
                "name": "demo",
                "login": "demo_user",
                "email": "demo1@yourcompany.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            project_user_group.id,
                        ],
                    )
                ],
            }
        )
        cls.demo_user2 = cls.res_users_obj.create(
            {
                "name": "demo2",
                "login": "demo_user2",
                "email": "demo2@yourcompany.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            project_user_group.id,
                        ],
                    )
                ],
            }
        )

        cls.demo_user3 = cls.res_users_obj.create(
            {
                "name": "demo3",
                "login": "demo_user3",
                "email": "demo3@yourcompany.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            project_user_group.id,
                        ],
                    )
                ],
            }
        )

        cls.demo_user4 = cls.res_users_obj.create(
            {
                "name": "demo4",
                "login": "demo_user4",
                "email": "demo4@yourcompany.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            project_user_group.id,
                        ],
                    )
                ],
            }
        )
        cls.user_manager = cls.res_users_obj.create(
            {
                "name": "User Officer",
                "login": "user_manager",
                "email": "usermanager@test.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            project_manager_group.id,
                        ],
                    )
                ],
            }
        )

        cls.mail_activity_a = cls.mail_activity_type_obj.create(
            {
                "name": "activity_a",
                "default_user_id": cls.demo_user.id,
                "summary": "summary",
            }
        )
        cls.mail_activity_b = cls.mail_activity_type_obj.create(
            {
                "name": "activity_b",
                "default_user_id": cls.demo_user.id,
            }
        )

        cls.project_1 = cls.project_project_obj.create(
            {
                "name": "Project #1",
                "user_id": cls.user_manager.id,
                "type_ids": [
                    (4, cls.stage_a.id),
                    (4, cls.stage_b.id),
                ],
            }
        )

        cls.project_2 = cls.project_project_obj.create(
            {
                "name": "Project #2",
                "user_id": cls.demo_user.id,
                "type_ids": [(4, cls.stage_b.id)],
            }
        )

        cls.task_1 = cls.project_task_obj.create(
            {
                "name": "Task 1",
                "project_id": cls.project_1.id,
                "description": "Test description",
                "user_ids": [(4, cls.demo_user2.id)],
            }
        )

        cls.task_2 = cls.project_task_obj.create(
            {
                "name": "Task 1",
                "project_id": cls.project_2.id,
                "description": "Test description",
                "user_ids": [(4, cls.demo_user2.id)],
            }
        )
