# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tests.common import SavepointCase


class TestProjectTaskTemplate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create tag model
        tag_model = cls.env["project.tags"]
        # creating tags: Red, Green, Blue, White, Yellow
        cls.tag_red = tag_model.create({"name": "Red"})
        cls.tag_green = tag_model.create({"name": "Green"})
        cls.tag_blue = tag_model.create({"name": "Blue"})
        cls.tag_white = tag_model.create({"name": "White"})
        cls.tag_yellow = tag_model.create({"name": "Yellow"})
        cls.stage_1 = cls.env["project.task.type"].create({"name": "Stage 1"})
        cls.stage_2 = cls.env["project.task.type"].create({"name": "Stage 2"})
        # create res users model
        res_users_model = cls.env["res.users"]
        # create users: Bob, Mike, Kate
        cls.user_bob = res_users_model.create(
            {"name": "Bob", "email": "bob@example.com", "login": "bob"}
        )
        cls.user_mike = res_users_model.create(
            {"name": "Mike", "email": "mike@example.com", "login": "mike"}
        )
        cls.user_kate = res_users_model.create(
            {"name": "Kate", "email": "kate@example.com", "login": "kate"}
        )
        # create task template model
        task_template_model = cls.env["project.task.template"]
        # create task templates:

        cls.template_1 = task_template_model.create(
            {
                "name": "Template1",
                "tag_ids": [
                    cls.tag_red.id,
                    cls.tag_green.id,
                ],
                "user_id": cls.user_bob.id,
                "description": "This is template 1",
            }
        )
        cls.template_2 = task_template_model.create(
            {
                "name": "Template2",
                "tag_ids": [
                    cls.tag_blue.id,
                    cls.tag_white.id,
                ],
                "user_id": cls.user_mike.id,
                "description": "This is template 2",
            }
        )
        # create project model
        project_model = cls.env["project.project"]
        # create projects : "Project 1" and add templates 1-2
        cls.project_1 = project_model.create(
            {
                "name": "Project 1",
                "task_template_ids": [cls.template_1.id, cls.template_2.id],
            }
        )

        cls.project_2 = project_model.create(
            {
                "name": "Project 1",
                "task_template_ids": [cls.template_1.id, cls.template_2.id],
                "default_task_template_id": cls.template_2.id,
                "template_task_type_ids": [cls.stage_1.id, cls.stage_2.id],
                "is_restrict_template_by_stages": True,
            }
        )
        # create task model
        cls.project_task_model = cls.env["project.task"]
        cls.test_task_1 = cls.project_task_model.create(
            {
                "name": "Test task 1",
                "user_id": cls.user_kate.id,
                "tag_ids": [
                    cls.tag_yellow.id,
                ],
                "description": "This is task1",
                "task_template_id": False,
            }
        )

        cls.test_project_2_task_1 = cls.project_task_model.create(
            {
                "name": "Test Project #2 Task #1",
                "user_id": cls.user_kate.id,
                "tag_ids": [
                    cls.tag_yellow.id,
                ],
                "description": "This is task1",
                "project_id": cls.project_2.id,
                "stage_id": cls.stage_1.id,
            }
        )

    def test_task_1_template_1(self):
        """Test the behavior when choosing a template."""
        # Set the task_template_id of test_task_1 to template_1.id
        self.test_task_1.task_template_id = self.template_1.id

        # Trigger the _onchange_task_template_id method
        self.test_task_1._onchange_task_template_id()

        # Verify that the user_id of test_task_1 is equal to the user_id of template_1
        self.assertEqual(
            self.test_task_1.user_id.id,
            self.template_1.user_id.id,
            msg="The task 1 user #id must be equal to the template 1 user ID#%s"
            % self.template_1.user_id.id,
        )

        # Verify that the tag_ids of test_task_1 are equal to the tag_ids of template_1
        self.assertEqual(
            self.test_task_1.tag_ids.ids,
            self.template_1.tag_ids.ids,
            msg="The task 1 tag IDs must be equal to the template 1 tag IDs",
        )

        # Verify that the description of test_task_1 is
        # equal to the description of template_1
        self.assertEqual(
            self.test_task_1.description,
            self.template_1.description,
            msg="The task 1 description must be equal to the template 1 description",
        )

    def test_task_1_template_2(self):
        """Test the behavior when choosing a different template (template_2)."""
        # Set the task_template_id of test_task_1 to template_2.id
        self.test_task_1.task_template_id = self.template_2.id

        # Trigger the _onchange_task_template_id method
        self.test_task_1._onchange_task_template_id()

        # Verify that the user_id of test_task_1 is equal to the user_id of template_2
        self.assertEqual(
            self.test_task_1.user_id.id,
            self.template_2.user_id.id,
            msg="The task 1 user #id must be equal to the template 2 user ID# %s"
            % self.template_2.user_id.id,
        )

        # Verify that the tag_ids of test_task_1 are equal to the tag_ids of template_2
        self.assertEqual(
            self.test_task_1.tag_ids.ids,
            self.template_2.tag_ids.ids,
            msg="The task 1 tag IDs must be equal to the template 2 tag IDs",
        )

        # Verify that the description of test_task_1 is
        # equal to the description of template_2
        self.assertEqual(
            self.test_task_1.description,
            self.template_2.description,
            msg="The task 1 description must be equal to the template 2 description",
        )

    def test_task_1_template_false(self):
        """Test the behavior when setting task_template_id to False
        after choosing a template.
        """
        # Set the task_template_id of test_task_1 to template_2.id
        self.test_task_1.task_template_id = self.template_2.id

        # Trigger the _onchange_task_template_id method
        self.test_task_1._onchange_task_template_id()

        # Set the task_template_id of test_task_1 to False
        self.test_task_1.task_template_id = False

        # Trigger the _onchange_task_template_id method
        self.test_task_1._onchange_task_template_id()

        # Verify that the user_id of test_task_1 is
        # equal to the user_id of template_2
        self.assertEqual(
            self.test_task_1.user_id.id,
            self.template_2.user_id.id,
            msg="The task 1 user #id must be equal to the template 2 user ID#%s"
            % self.template_2.user_id.id,
        )

        # Verify that the tag_ids of test_task_1 are equal to the tag_ids of template_2
        self.assertEqual(
            self.test_task_1.tag_ids.ids,
            self.template_2.tag_ids.ids,
            msg="The task 1 tag IDs must be equal to the template 2 tag IDs",
        )

        # Verify that the description of test_task_1 is
        # equal to the description of template_2
        self.assertEqual(
            self.test_task_1.description,
            self.template_2.description,
            msg="The task 1 description must be equal to the template 2 description",
        )

    def test_task_2_template_2(self):
        """Test the behavior when choosing a default template in project settings."""

        self.assertTrue(
            self.test_project_2_task_1.task_template_id,
            msg=f"The task template ID #{self.template_2.id} must be set",
        )

        self.assertEqual(
            self.test_project_2_task_1.task_template_id.id,
            self.project_2.default_task_template_id.id,
            msg=(
                "The task template ID must be equal"
                "to the default template ID in project settings"
            ),
        )

        self.project_2.task_template_ids = [self.template_1.id]
        self.project_2._onchange_task_template_ids()
        self.assertFalse(self.project_2.default_task_template_id, msg="Must be empty")

    def test_change_stage(self):
        """Test the behavior when changing the stage of a task."""

        self.assertTrue(
            self.test_project_2_task_1.task_template_id,
            msg=f"The task template ID #{self.template_2.id} must be set",
        )

        self.assertEqual(
            self.test_project_2_task_1.task_template_id.id,
            self.project_2.default_task_template_id.id,
            msg=(
                "The task template ID must be equal"
                "to the default template ID in project settings"
            ),
        )

        self.test_project_2_task_1.stage_id = self.stage_2.id
        self.test_project_2_task_1._compute_template_visible()
        self.assertEqual(
            self.test_project_2_task_1.task_template_id.id,
            self.project_2.default_task_template_id.id,
            msg=(
                "The task template ID must be equal"
                "to the default template ID in project settings"
            ),
        )
