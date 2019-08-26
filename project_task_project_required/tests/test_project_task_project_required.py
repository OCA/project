# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestProjectTaskProjectRequired(TransactionCase):

    def setUp(self):
        super().setUp()

        self.Project = self.env['project.project']
        self.ProjectTask = self.env['project.task']

        self.project = self.Project.create({
            'name': 'Project',
        })

    def test_project_required(self):
        self.env.user.company_id.is_project_task_project_required = True
        with self.assertRaises(ValidationError):
            self.ProjectTask.create({
                'name': 'Task A',
            })
        self.ProjectTask.create({
            'name': 'Task B',
            'project_id': self.project.id,
        })

    def test_project_not_required(self):
        self.env.user.company_id.is_project_task_project_required = False
        self.ProjectTask.create({
            'name': 'Task A',
        })
        self.ProjectTask.create({
            'name': 'Task B',
            'project_id': self.project.id,
        })
