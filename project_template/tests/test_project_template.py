# Copyright 2019 Patrick Wilson <patrickraymondwilson@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo.tests import Form

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

    def test_onchange_project_template_copies_project_settings(self):
        """selecting a project template copies project settings in the form"""
        project = self.test_project
        project.is_template = True
        project.label_tasks = "Deliverables"
        project.allow_milestones = True
        project.allow_task_dependencies = True
        project.privacy_visibility = "employees"

        project_form = Form(self.env["project.project"])
        project_form.name = "Project from selector"
        project_form.project_template_id = project
        self.assertEqual(project_form.label_tasks, project.label_tasks)
        self.assertEqual(project_form.privacy_visibility, project.privacy_visibility)
        self.assertEqual(project_form.allow_milestones, project.allow_milestones)

    def test_create_project_with_template_copies_project_data_and_template_tasks(self):
        """creating a project with a template copies settings and reusable tasks"""
        project = self.test_project
        project.is_template = True
        project.label_tasks = "Deliverables"
        project.privacy_visibility = "employees"
        project.allow_task_dependencies = True
        self.tasks[0].is_template = True
        self.tasks[1].is_template = False

        new_project = self.env["project.project"].create(
            {"name": "Project from selector", "project_template_id": project.id}
        )

        self.assertEqual(new_project.label_tasks, project.label_tasks)
        self.assertEqual(new_project.privacy_visibility, project.privacy_visibility)
        self.assertEqual(
            new_project.allow_task_dependencies, project.allow_task_dependencies
        )
        self.assertEqual(new_project.task_ids.mapped("name"), [self.tasks[0].name])
        self.assertFalse(new_project.task_ids.is_template)

    def test_create_project_with_template_preserves_explicit_values(self):
        """explicit create values are not overwritten by template defaults"""
        project = self.test_project
        project.is_template = True
        project.label_tasks = "Deliverables"
        project.privacy_visibility = "employees"

        new_project = self.env["project.project"].create(
            {
                "name": "Project from selector",
                "project_template_id": project.id,
                "label_tasks": "Tasks",
                "privacy_visibility": "followers",
            }
        )

        self.assertEqual(new_project.label_tasks, "Tasks")
        self.assertEqual(new_project.privacy_visibility, "followers")

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
        self.assertFalse(new_project.is_template)

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
            task.is_template = True
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

    def test_create_project_from_template_only_copies_template_tasks(self):
        project = self.test_project
        project.is_template = True
        self.tasks[0].is_template = True
        self.tasks[1].is_template = False
        child_to_copy = self.env["project.task"].create(
            {
                "name": "Copied child",
                "project_id": project.id,
                "parent_id": self.tasks[0].id,
                "is_template": True,
            }
        )
        child_to_skip = self.env["project.task"].create(
            {
                "name": "Skipped child",
                "project_id": project.id,
                "parent_id": self.tasks[0].id,
                "is_template": False,
            }
        )

        project.create_project_from_template()
        new_project = self.env["project.project"].search(
            [("name", "=", "TestProject (COPY)")]
        )
        self.assertEqual(len(new_project), 1)
        new_tasks = self.env["project.task"].search(
            [("project_id", "=", new_project.id)]
        )
        self.assertCountEqual(
            new_tasks.mapped("name"), [self.tasks[0].name, child_to_copy.name]
        )
        self.assertNotIn(child_to_skip.name, new_tasks.mapped("name"))
        self.assertFalse(any(new_tasks.mapped("is_template")))

    def test_create_project_from_template_copies_nested_template_tasks(self):
        """project templates copy nested reusable task trees"""
        project = self.env["project.project"].create(
            {"name": "Nested Template", "is_template": True}
        )
        root = self.env["project.task"].create(
            {"name": "Copied root", "project_id": project.id, "is_template": True}
        )
        child = self.env["project.task"].create(
            {
                "name": "Copied child",
                "project_id": project.id,
                "parent_id": root.id,
                "is_template": True,
            }
        )
        grandchild = self.env["project.task"].create(
            {
                "name": "Copied grandchild",
                "project_id": project.id,
                "parent_id": child.id,
                "is_template": True,
            }
        )

        project.create_project_from_template()

        new_project = self.env["project.project"].search(
            [("name", "=", "Nested Template (COPY)")]
        )
        new_tasks = self.env["project.task"].search(
            [("project_id", "=", new_project.id)]
        )
        self.assertCountEqual(
            new_tasks.mapped("name"), [root.name, child.name, grandchild.name]
        )
        self.assertTrue(
            new_tasks.filtered(lambda task: task.name == child.name).parent_id
        )
        self.assertTrue(
            new_tasks.filtered(lambda task: task.name == grandchild.name).parent_id
        )
