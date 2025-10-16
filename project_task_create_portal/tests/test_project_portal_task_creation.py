# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserPortal
from odoo.addons.project.tests.test_access_rights import TestProjectPortalCommon


@tagged("post_install", "-at_install")
class TestProjectPortalTaskCreation(TestProjectPortalCommon, HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super(TestProjectPortalTaskCreation, cls).setUpClass()

        # Create test project
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "description": "Test project for portal task creation",
            }
        )

        # Create test stages
        cls.stage_backlog = cls.env["project.task.type"].create(
            {
                "name": "Backlog",
                "project_ids": [(6, 0, [cls.project.id])],
            }
        )

        cls.stage_in_progress = cls.env["project.task.type"].create(
            {
                "name": "In Progress",
                "project_ids": [(6, 0, [cls.project.id])],
            }
        )

        # Set portal task creation stage
        cls.project.portal_stage_id = cls.stage_backlog

        # Set portal allowed users
        cls.project.portal_user_ids = cls.user_portal

    def test_project_portal_task_creation_stage_constraint(self):
        """Test that portal task creation stage must belong to the project."""
        # Create another project
        other_project = self.env["project.project"].create(
            {
                "name": "Other Project",
            }
        )

        # Create stage for other project
        other_stage = self.env["project.task.type"].create(
            {
                "name": "Other Stage",
                "project_ids": [(6, 0, [other_project.id])],
            }
        )

        # Try to set stage from other project
        with self.assertRaises(ValidationError):
            self.project.portal_stage_id = other_stage

    def test_project_portal_task_creation_allowed(self):
        """Test project portal task creation allowed check."""
        # Project with portal stage should allow creation
        user_project = self.project.with_user(self.user_portal).sudo()
        self.assertTrue(user_project.is_portal_task_creation_allowed())

        # Project without portal stage should not allow creation
        self.project.portal_stage_id = False
        self.assertFalse(user_project.is_portal_task_creation_allowed())

        self.project.portal_stage_id = self.stage_backlog
        self.project.portal_user_ids = False
        self.assertFalse(user_project.is_portal_task_creation_allowed())

    def test_task_portal_creation(self):
        """Test task creation by portal user."""
        # Create task as portal user
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .sudo()
            .create(
                {
                    "name": "Portal Task",
                    "description": "Task created by portal user",
                    "project_id": self.project.id,
                }
            )
        )

        # Check that task was created with correct settings
        self.assertEqual(task.name, "Portal Task")
        self.assertEqual(task.project_id, self.project)
        self.assertEqual(task.stage_id, self.stage_backlog)
        self.assertEqual(task.create_uid, self.user_portal)

    def test_task_portal_creation_without_allowed_project(self):
        """Test task creation by portal user in project without portal stage."""
        # Remove portal stage from project
        self.project.portal_stage_id = False

        # Try to create task as portal user
        with self.assertRaises(AccessError):
            self.env["project.task"].with_user(self.user_portal).sudo().create(
                {
                    "name": "Portal Task",
                    "description": "Task created by portal user",
                    "project_id": self.project.id,
                }
            )

    def test_task_portal_edit_own_task(self):
        """Test portal user editing their own task."""
        # Create task as portal user
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .sudo()
            .create(
                {
                    "name": "Portal Task",
                    "description": "Task created by portal user",
                    "project_id": self.project.id,
                }
            )
        )

        # Edit task as portal user
        task.with_user(self.user_portal).sudo().write(
            {
                "name": "Updated Portal Task",
                "description": "Updated description",
            }
        )

        # Check that task was updated
        self.assertEqual(task.name, "Updated Portal Task")
        self.assertIn("Updated description", task.description)

    def test_task_portal_edit_other_user_task(self):
        """Test portal user trying to edit another user's task."""
        # Create task as internal user
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .sudo()
            .create(
                {
                    "name": "Internal Task",
                    "description": "Task created by internal user",
                    "project_id": self.project.id,
                }
            )
        )

        self.project.portal_user_ids = False

        # Try to edit task as portal user
        with self.assertRaises(AccessError):
            task.with_user(self.user_portal).sudo().write(
                {
                    "name": "Hacked Task",
                }
            )

    def test_task_portal_edit_wrong_stage(self):
        """Test portal user trying to edit task in wrong stage."""
        # Create task as portal user
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .sudo()
            .create(
                {
                    "name": "Portal Task",
                    "description": "Task created by portal user",
                    "project_id": self.project.id,
                }
            )
        )

        # Move task to different stage
        task.stage_id = self.stage_in_progress

        # Try to edit task as portal user
        with self.assertRaises(AccessError):
            task.with_user(self.user_portal).write(
                {
                    "name": "Updated Task",
                }
            )
