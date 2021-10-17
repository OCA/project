from odoo.tests.common import TransactionCase


class TestPullRequestState(TransactionCase):
    def setUp(self):
        super(TestPullRequestState, self).setUp()

        ProjectProject = self.env["project.project"]
        ProjectTask = self.env['project.task']

        self.project_1 = ProjectProject.create({
            'name': 'Test Project',
            'pr_required_states': [(4, 6, 0)],
            'key': 'ABC',
            'pr_state_default': None

        })
        self.project_2 = ProjectProject.create({
            'name': 'Test Project',
            'pr_required_states': [(4, 6, 0), (4, 5, 0)],
            'key': 'DEF',
            'pr_state_default': 'draft'
        })
        self.task_1 = ProjectTask.create({
            'name': 'Test Task',
            'project_id': self.project_1.id,
            'pr_uri': None
        })
        self.task_2 = ProjectTask.create({
            'name': 'Test Task',
            'project_id': self.project_2.id,
            'pr_uri': False
        })

    def test_pull_request_state(self):
        """Testing project task pull request states"""
        self.task_1.write({
            'pr_uri': 'Test Pull Request'
        })
        self.assertEquals(self.task_1.pr_state, self.project_1.pr_state_default,
                          msg='Pull Request State must be equal PR state in project')
        self.task_2.pr_uri = False
        self.assertEquals(self.task_2.pr_state, False,
                          msg='Pull Request State must be equal False')
        self.task_2.pr_uri = 'Test 2'
        self.task_2.pr_state = 'merged'
        self.assertEquals(self.task_2.pr_state, 'merged',
                          msg='Pull Request State must be equal Merged')
        task = self.env['project.task']
        self.task_3 = task.create({
            'name': 'Test Task',
            'project_id': False,
            'pr_uri': False
        })
        self.assertEquals(self.task_3.pr_state, False,
                          msg='Pull Request State must be equal False')
        self.task_4 = task.create({
            'name': 'Test Task',
            'project_id': False,
            'pr_uri': 'Test URI'
        })
        self.assertEquals(self.task_4.pr_state, False,
                          msg='Pull Request State must be equal False')
        self.task_5 = task.create({
            'name': 'Test Task',
            'project_id': self.project_2.id,
            'pr_uri': 'Test'
        })
        self.assertEquals(self.task_5.pr_state, 'draft',
                          msg='Pull Request State must be equal Draft')
