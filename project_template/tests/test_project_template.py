# Copyright 2019 Patrick Wilson <patrickraymondwilson@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo.addons.base.tests.common import BaseCommon


class TestProjectTemplate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_customer = cls.env["res.partner"].create({"name": "TestCustomer"})
        cls.test_project = cls.env["project.project"].create(
            {
                "name": "TestProject",
                "alias_name": "test_alias",
                "partner_id": cls.test_customer.id,
            }
        )
        cls.tasks = [
            cls.env["project.task"].create(
                {"name": "TestTask", "project_id": cls.test_project.id}
            ),
            cls.env["project.task"].create(
                {"name": "TestTask2", "project_id": cls.test_project.id}
            ),
        ]

    # TEST 01: Set project to be a template and test name change
    def test_on_change_is_template(self):
        # Test when changing project to a template
        project_01 = self.test_project
        project_01.is_template = True
        project_01.on_change_is_template()
        self.assertEqual(project_01.name, "TestProject (TEMPLATE)")

        # Test when changing template back to project
        project_01.is_template = False
        project_01.on_change_is_template()
        self.assertEqual(project_01.name, "TestProject")

    # TEST 02: Create project from template
    def test_create_project_from_template(self):
        # Set Project Template
        project_01 = self.test_project
        project_01.is_template = True
        project_01.on_change_is_template()

        # Create new Project from Template
        project_01.create_project_from_template()
        new_project = self.env["project.project"].search(
            [("name", "=", "TestProject (COPY)")]
        )
        self.assertEqual(len(new_project), 1)

    # TEST 03: Create project from template using non-standard name
    def test_create_project_from_template_non_standard_name(self):
        # Set Project Template
        project_01 = self.test_project
        project_01.is_template = True
        project_01.on_change_is_template()
        # Change the name of project template
        project_01.name = "TestProject(TEST)"

        # Create new Project from Template
        project_01.create_project_from_template()
        new_project = self.env["project.project"].search(
            [("name", "=", "TestProject(TEST) (COPY)")]
        )
        self.assertEqual(len(new_project), 1)

    def test_create_project_from_template_duplicate_task_names(self):
        """Check names and dates on generated project"""
        project_01 = self.test_project
        project_01.is_template = True
        project_01.on_change_is_template()
        # Set the same name on all tasks
        dates = set()
        now = datetime.now()
        for i, task in enumerate(self.tasks):
            date = now - timedelta(weeks=i)
            task.name = "Same for all tasks"
            dates.add(date)
            task.date_end = date

        # Create new Project from Template
        project_01.create_project_from_template()
        new_project = self.env["project.project"].search(
            [("name", "=", "TestProject (COPY)")]
        )
        self.assertEqual(len(new_project), 1)
        new_tasks = self.env["project.task"].search(
            [
                ("project_id", "=", new_project.id),
            ]
        )
        self.assertEqual(len(new_tasks), len(self.tasks))
        self.assertEqual(set(new_tasks.mapped("date_end")), dates)

        # When making a regular copy of the project, the dates are cleared
        # as per project.task::update_date_end
        regular_copy = project_01.copy()
        tasks = regular_copy.task_ids
        self.assertEqual(len(tasks), 2)
        self.assertFalse(tasks[0].date_end)
        self.assertFalse(tasks[1].date_end)
