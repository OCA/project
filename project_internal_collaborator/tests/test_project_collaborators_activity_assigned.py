from odoo import fields

from .common import TestProjectCollaboratorCommon


class TestProjectCollaboratorsTaskAssigned(TestProjectCollaboratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        config = cls.config_obj.create(
            {
                "collaborators_activity_assigned": True,
                "collaborators_task_assigned": False,
            }
        )
        config.execute()

    def test_get_collaborator_config_parameters(self):
        """
        Test if the configuration parameters for collaborators
        task and activity assigned are retrieved correctly.
        """
        (
            collaborators_task_assigned,
            collaborators_activity_assigned,
        ) = self.project_project_obj.get_collaborator_config_parameters()
        self.assertFalse(
            collaborators_task_assigned,
            msg="Collaborators task assigned parameter should be False",
        )
        self.assertTrue(
            collaborators_activity_assigned,
            msg="Collaborators activity assigned parameter should be True",
        )

        (
            collaborators_task_assigned,
            collaborators_activity_assigned,
        ) = self.task_1.project_id.get_collaborator_config_parameters()
        self.assertFalse(
            collaborators_task_assigned,
            msg="Collaborators task assigned parameter should be False",
        )
        self.assertTrue(
            collaborators_activity_assigned,
            msg="Collaborators activity assigned parameter should be True",
        )

    def test_add_assigned_user_to_task(self):
        """
        Сheck if the assigned user is added to the task,
        but not to the list of co-authors.
        """

        self.task_2.user_ids = [(4, self.demo_user3.id)]
        self.assertNotIn(
            self.demo_user3,
            self.task_2.project_id.internal_collaborator_ids,
            msg="The user should be added to the list of co-authors of the project",
        )

        activity = self.task_2.activity_schedule(
            activity_type_id=self.mail_activity_b.id,
            user_id=self.demo_user4.id,
            note="Fix the bug",
            summary="Fix the bug",
            date_deadline=fields.Date.today(),
        )

        self.assertIn(
            self.demo_user4,
            self.task_2.project_id.internal_collaborator_ids,
            msg="The user should be added to the list of co-authors of the project",
        )

        activity.action_feedback()
        self.assertNotIn(
            self.demo_user4,
            self.task_2.project_id.internal_collaborator_ids,
            msg="The user should be added to the list of co-authors of the project",
        )
        self.project_2.message_subscribe(self.demo_user4.partner_id.ids)

        activity = self.task_2.activity_schedule(
            activity_type_id=self.mail_activity_b.id,
            user_id=self.demo_user4.id,
            note="Fix the bug",
            summary="Fix the bug",
            date_deadline=fields.Date.today(),
        )
        self.assertNotIn(
            self.demo_user4,
            self.task_2.project_id.internal_collaborator_ids,
            msg="The user should be added to the list of co-authors of the project",
        )
