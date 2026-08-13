# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestProjectTaskProjectRequired(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Project = cls.env["project.project"]
        cls.ProjectTask = cls.env["project.task"]

        cls.project = cls.Project.create(
            {
                "name": "Project",
            }
        )

    def test_project_required(self):
        self.env.company.is_project_task_project_required = True
        with self.assertRaises(ValidationError):
            self.ProjectTask.create(
                {
                    "name": "Task A",
                }
            )
        self.ProjectTask.create(
            {
                "name": "Task B",
                "project_id": self.project.id,
            }
        )

    def test_project_not_required(self):
        self.env.company.is_project_task_project_required = False
        self.ProjectTask.create(
            {
                "name": "Task A",
            }
        )
        self.ProjectTask.create(
            {
                "name": "Task B",
                "project_id": self.project.id,
            }
        )
