# Copyright 2022 Moduon - Eduardo de Miguel <edu@moduon.team>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestAutoFoldPersonalStages(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user_group_employee = cls.env.ref("base.group_user")
        user_group_project_user = cls.env.ref("project.group_project_user")
        user_group_project_manager = cls.env.ref("project.group_project_manager")
        cls.partner_1 = cls.env["res.partner"].create(
            {"name": "Valid Lelitre", "email": "valid.lelitre@agrolait.com"}
        )
        # Test users to use through the various tests
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.user_projectuser = Users.create(
            {
                "name": "Armande ProjectUser",
                "login": "armandel",
                "password": "armandel",
                "email": "armande.projectuser@example.com",
                "groups_id": [
                    (6, 0, [user_group_employee.id, user_group_project_user.id])
                ],
            }
        )
        cls.user_projectmanager = Users.create(
            {
                "name": "Bastien ProjectManager",
                "login": "bastien",
                "email": "bastien.projectmanager@example.com",
                "groups_id": [
                    (6, 0, [user_group_employee.id, user_group_project_manager.id])
                ],
            }
        )
        # Test 'Pigs' project
        cls.project_pigs = (
            cls.env["project.project"]
            .with_context(mail_create_nolog=True)
            .create(
                {
                    "name": "Pigs",
                    "privacy_visibility": "employees",
                    "alias_name": "project+pigs",
                    "partner_id": cls.partner_1.id,
                }
            )
        )
        cls.project_task_stages = cls.env["project.task.type"].create(
            [
                {"sequence": 1, "name": "New"},
                {"sequence": 2, "name": "In progress"},
                {"sequence": 3, "name": "Finished", "fold": True},
                {"sequence": 4, "name": "Canceled", "fold": True},
            ]
        )
        cls.project_pigs.type_ids = [(6, 0, cls.project_task_stages.ids)]
        cls.task_3 = cls.env["project.task"].create(
            {
                "name": "Multiple Assigned Task",
                "user_ids": [
                    (6, 0, [cls.user_projectmanager.id, cls.user_projectuser.id])
                ],
                "project_id": cls.project_pigs.id,
            }
        )
        cls.task_3.with_user(cls.user_projectmanager)._compute_personal_stage_id()
        cls.task_3.with_user(cls.user_projectuser)._compute_personal_stage_id()

    def setUp(self):
        """Save user_projectuser initial personal stage"""
        super().setUp()
        self.task_3_projectuser_initial_personal_stage = self.task_3.with_user(
            self.user_projectuser
        ).personal_stage_id.stage_id

    def tearDown(self):
        """Personal Stage no other assignees shouldn't be modified

        Personal Stage on other Task assignees shouldn't be modified
        by the actions of the user that performs task closing.
        """
        super().tearDown()
        self.assertEqual(
            self.task_3_projectuser_initial_personal_stage,
            self.task_3.with_user(self.user_projectuser).personal_stage_id.stage_id,
            "Personal Stage on other assignees has been modified",
        )

    def test_personal_stage_not_change(self):
        """Personal Stage don't change

        Personal stage don't change if task stage is not on a closing stage.
        """
        target_task_stage = self.project_task_stages[1]  # In progress stage
        old_personal_stage = self.task_3.with_user(
            self.user_projectmanager
        ).personal_stage_id.stage_id
        self.task_3.with_user(self.user_projectmanager).stage_id = target_task_stage.id
        new_personal_stage = self.task_3.with_user(
            self.user_projectmanager
        ).personal_stage_id.stage_id
        self.assertEqual(old_personal_stage, new_personal_stage)

    def test_personal_stage_changes_to_one_with_the_same_name(self):
        """Personal Stage changes to the same name as Task Stage

        Personal stage change if task stage is on a closing stage and changes
        to the one with the same name of the task stage.
        """
        target_task_stage = self.project_task_stages[3]  # Canceled stage
        self.task_3.with_user(self.user_projectmanager).stage_id = target_task_stage.id
        new_personal_stage = self.task_3.with_user(
            self.user_projectmanager
        ).personal_stage_id.stage_id
        self.assertEqual(new_personal_stage.name, target_task_stage.name)

    def test_personal_stage_changes_to_first_personal_closing_stage(self):
        """Personal Stage changes to the first closing or folded stage

        Personal stage changes to a closing or fold stage
        if task stage is on a closing stage
        and the name of the personal stage is not found.
        """
        personal_target_closing_stage = self.env["project.task.type"].search(
            [
                ("user_id", "=", self.user_projectmanager.id),
                ("fold", "=", True),
            ],
            order="fold desc",
            limit=1,
        )
        target_task_stage = self.project_task_stages[2]  # Finished stage
        self.task_3.with_user(self.user_projectmanager).stage_id = target_task_stage.id
        new_personal_stage = self.task_3.with_user(
            self.user_projectmanager
        ).personal_stage_id.stage_id
        self.assertEqual(new_personal_stage, personal_target_closing_stage)
