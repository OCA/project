# Copyright Cetmix OU 2023
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).
from odoo.tests.common import TransactionCase


class TestPullRequestState(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Project = cls.env["project.project"]
        cls.Task = cls.env["project.task"]
        cls.Stage = cls.env["project.task.type"]

        cls.stage_draft = cls.Stage.create({"name": "Draft"})
        cls.stage_progress = cls.Stage.create({"name": "Progress"})

        # Used to set res config settings
        cls.res_config = cls.env["res.config.settings"]

        cls.project_1 = cls.Project.create(
            {
                "name": "Test Project 1",
                "type_ids": [(4, cls.stage_draft.id), (4, cls.stage_progress.id)],
                "pr_state_default": "draft",
            }
        )
        cls.project_2 = cls.Project.create(
            {
                "name": "Test Project 2",
                "type_ids": [(4, cls.stage_draft.id), (4, cls.stage_progress.id)],
                "pr_state_default": "open",
            }
        )
        cls.project_3 = cls.Project.create(
            {
                "name": "Test Project 3",
                "type_ids": [(4, cls.stage_draft.id), (4, cls.stage_progress.id)],
            }
        )
        cls.task_1 = cls.Task.create(
            {
                "name": "Test Task for project 1",
                "project_id": cls.project_1.id,
            }
        )
        cls.task_2 = cls.Task.create(
            {
                "name": "Test Task for project 2",
                "project_id": cls.project_2.id,
            }
        )
        cls.task_3 = cls.Task.create(
            {
                "name": "Test Task without project",
            }
        )

    def _set_default_pr_state(self, state):
        """Set the default pull request state.

        :param state(str): The default state for pull requests.

        :return: The result of executing the record creation operation.
        """
        return self.res_config.create({"pr_state_default": state}).execute()

    def test_pull_request_state_set_default(self):
        """Set default PR state from project when PR URI is added to task"""

        # Set default PR state
        self._set_default_pr_state("closed")

        # Set to several existing tasks at once
        tasks = self.Task.browse([self.task_1.id, self.task_2.id, self.task_3.id])
        tasks.write({"pr_uri": "https://@my.pr.uri/pr"})

        self.assertEqual(self.task_1.pr_state, "draft", "PR state must be 'draft'")
        self.assertEqual(self.task_2.pr_state, "open", "PR state must be 'open'")
        self.assertEqual(self.task_3.pr_state, "closed", "PR state must be 'closed'")

        # Change pr_state
        tasks.write({"pr_state": "closed"})

        self.assertEqual(self.task_1.pr_state, "closed", "PR state must be 'closed'")
        self.assertEqual(self.task_2.pr_state, "closed", "PR state must be 'closed'")
        self.assertEqual(self.task_3.pr_state, "closed", "PR state must be 'closed'")

    def test_pull_request_state_set_explicit(self):
        """Set PR state from vals when PR URI is added to task"""
        # Set to several existing tasks at once
        tasks = self.Task.browse([self.task_1.id, self.task_2.id, self.task_3.id])
        tasks.write({"pr_uri": "https://@my.pr.uri/pr", "pr_state": "merged"})

        self.assertEqual(self.task_1.pr_state, "merged", "PR state must be 'merged'")
        self.assertEqual(self.task_2.pr_state, "merged", "PR state must be 'merged'")
        self.assertEqual(self.task_3.pr_state, "merged", "PR state must be 'merged'")

    def test_create_task_with_uri(self):
        """Add PR URI when task created"""
        task_with_uri = self.Task.create(
            {
                "name": "Test Task with URI",
                "project_id": self.project_2.id,
                "pr_uri": "https://@my.pr.uri/pr",
            }
        )
        self.assertEqual(task_with_uri.pr_state, "open", "PR state must be 'open'")

    def test_multi_create(self):
        """Create several tasks at the one time"""
        self._set_default_pr_state("closed")
        test_tasks_data = [
            {
                "name": "Test Task 1",
                "project_id": self.project_1.id,
                "pr_uri": "https://@my.pr.uri/pr",
            },
            {
                "name": "Test Task 2",
                "project_id": self.project_2.id,
                "pr_uri": "https://@my.pr.uri/pr",
            },
            {
                "name": "Test Task 3",
                "project_id": self.project_3.id,
                "pr_uri": "https://@my.pr.uri/pr",
            },
        ]
        test_tasks = self.Task.create(test_tasks_data)

        self.assertEqual(test_tasks[0].pr_state, "draft", "PR state must be 'draft'")
        self.assertEqual(test_tasks[1].pr_state, "open", "PR state must be 'open'")
        self.assertEqual(test_tasks[2].pr_state, "closed", "PR state must be 'closed'")

    def test_set_pr_state(self):
        """Test _set_pr_state function"""
        self.task_3.write({"pr_uri": "https://@my.pr.uri/pr"})
        self.assertFalse(self.task_3.pr_state, "PR state must be False")
        # Set system wide default PR state
        self._set_default_pr_state("closed")

        self.task_3.write({"pr_uri": "https://@my.pr.uri/new_pr"})
        self.assertEqual(self.task_3.pr_state, "closed", "PR state must be 'closed'")

        self.task_1.write({"pr_uri": "https://@my.pr.uri/pr"})
        self.assertEqual(self.task_1.pr_state, "draft", "PR state must be 'draft'")
        # Remove PR URI
        self.task_1.write({"pr_uri": ""})
        self.assertFalse(self.task_1.pr_state, "PR state must be False")

        # Create task for project without pr_state_default
        test_task = self.Task.create(
            {
                "name": "Test Task",
                "project_id": self.project_3.id,
                "pr_uri": "https://@my.pr.uri/pr",
            }
        )
        self.assertEqual(test_task.pr_state, "closed", "PR state must be 'closed'")

    def test_set_pr_state_default(self):
        """Set values for the pr_state_default parameter"""
        self.env["res.config.settings"].create(
            {
                "pr_state_default": "open",
            }
        ).execute()

        # Verify that the parameter has been set to the desired value
        pr_state_default_param = self.env["ir.config_parameter"].get_param(
            "project_task_pull_request_state.pr_state_default"
        )
        self.assertEqual(
            pr_state_default_param, "open", "PR state default parameter must be 'open'"
        )
