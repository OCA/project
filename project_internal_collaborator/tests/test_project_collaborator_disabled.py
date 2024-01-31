from .common import TestProjectCollaboratorCommon


class TestProjectCollaboratorsDisabled(TestProjectCollaboratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        config = cls.config_obj.create(
            {
                "collaborators_task_assigned": False,
                "collaborators_activity_assigned": False,
            }
        )
        config.execute()

    def test_get_collaborator_config_parameters(self):
        """
        Test case for get_collaborator_config_parameters method.

        It checks if the configuration parameters for collaborators
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
        self.assertFalse(
            collaborators_activity_assigned,
            msg="Collaborators activity assigned parameter should be False",
        )

        (
            collaborators_task_assigned,
            collaborators_activity_assigned,
        ) = self.task_1.project_id.get_collaborator_config_parameters()
        self.assertFalse(
            collaborators_task_assigned,
            msg="Collaborators task assigned parameter should be False",
        )
        self.assertFalse(
            collaborators_activity_assigned,
            msg="Collaborators activity assigned parameter should be False",
        )

    def test_add_assigned_user_to_task(self):
        """
        Сheck if the assigned user is added to the task, but not to the list of co-authors.
        """

        self.task_2.user_ids = [(4, self.demo_user3.id)]
        self.assertNotIn(
            self.demo_user3,
            self.task_2.project_id.internal_collaborator_ids,
            msg="Assigned user should not be added to the list of co-authors of the project",
        )
        self.assertEqual(
            len(self.project_2.internal_collaborator_ids),
            0,
            msg="Collaborator ids should be empty",
        )
