from odoo.tests.common import TransactionCase


class TestPullRequestState(TransactionCase):
    def setUp(self):
        super(TestPullRequestState, self).setUp()

        self.Project = self.env["project.project"]
        self.Task = self.env['project.task']
        self.Stage = self.env['project.task.type']

        self.stage_draft = self.Stage.create({"name": "Draft"})
        self.stage_progress = self.Stage.create({"name": "Progress"})
        
        self.project_1 = self.Project.create({
            'name': 'Test Project 1',
            "type_ids": [(4, self.stage_draft.id),(4, self.stage_progress.id)],
            'pr_state_default': "draft"
        })
        self.project_2 = self.Project.create({
            'name': 'Test Project 2',
            "type_ids": [(4, self.stage_draft.id),(4, self.stage_progress.id)],
            'pr_state_default': 'open'
        })
        self.task_1 = self.Task.create({
            'name': 'Test Task for project 1',
            'project_id': self.project_1.id,
        })
        self.task_2 = self.Task.create({
            'name': 'Test Task for project 2',
            'project_id': self.project_2.id,
        })
        self.task_3 = self.Task.create({
            'name': 'Test Task without project',
        })

    def test_pull_request_state_set_default(self):
        """Set default PR state from project when PR URI is added to task"""

        # Set to several existing tasks at once
        tasks = self.Task.browse([self.task_1.id, self.task_2.id, self.task_3.id])
        tasks.write({"pr_uri": "https://@my.pr.uri/pr"})

        self.assertEqual(self.task_1.pr_state, "draft", "PR state must be 'draft")
        self.assertEqual(self.task_2.pr_state, "open", "PR state must be 'open")
        self.assertFalse(self.task_3.pr_state, "PR state must not be set")

    def test_pull_request_state_set_explicit(self):
        """Set PR state from vals when PR URI is added to task"""
        # Set to several existing tasks at once
        tasks = self.Task.browse([self.task_1.id, self.task_2.id, self.task_3.id])
        tasks.write({"pr_uri": "https://@my.pr.uri/pr", "pr_state": "merged"})

        self.assertEqual(self.task_1.pr_state, "merged", "PR state must be 'merged")
        self.assertEqual(self.task_2.pr_state, "merged", "PR state must be 'merged")
        self.assertEqual(self.task_3.pr_state, "merged", "PR state must be 'merged")
