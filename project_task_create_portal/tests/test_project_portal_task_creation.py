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
                "privacy_visibility": "portal",
                "message_partner_ids": [(4, cls.user_portal.partner_id.id)],
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
            self.env["project.task"].with_user(self.user_portal).create(
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
            .create(
                {
                    "name": "Portal Task",
                    "description": "Task created by portal user",
                    "project_id": self.project.id,
                }
            )
        )

        # Edit task as portal user
        task.with_user(self.user_portal).write(
            {
                "name": "Updated Portal Task",
                "description": "Updated description",
            }
        )

        # Check that task was updated
        self.assertEqual(task.name, "Updated Portal Task")
        self.assertIn("Updated description", task.description)

    def test_task_portal_edit_rejects_forbidden_fields(self):
        """Test that portal users can edit only fields exposed by the form."""
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .create(
                {
                    "name": "Portal Task",
                    "description": "Task created by portal user",
                    "project_id": self.project.id,
                }
            )
        )

        for field_name, value in (
            ("stage_id", self.stage_in_progress.id),
            ("project_id", False),
            ("user_ids", [(6, 0, [self.env.ref("base.user_admin").id])]),
        ):
            with self.subTest(field_name=field_name), self.assertRaises(AccessError):
                task.with_user(self.user_portal).write({field_name: value})

    def test_task_portal_record_rule_rejects_other_users_task(self):
        """Test the portal record rule restricts writes to tasks owned by the user."""
        task = self.env["project.task"].create(
            {
                "name": "Internal Task",
                "description": "Task created by an internal user",
                "project_id": self.project.id,
                "stage_id": self.stage_backlog.id,
            }
        )

        with self.assertRaises(AccessError):
            task.with_user(self.user_portal).check_access_rule("write")

    def test_task_portal_edit_other_user_task(self):
        """Test portal user trying to edit another user's task."""
        # Create task as internal user
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
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
            task.with_user(self.user_portal).write(
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
            .create(
                {
                    "name": "Portal Task",
                    "description": "Task created by portal user",
                    "project_id": self.project.id,
                }
            )
        )

        # Move task to different stage
        task.sudo().stage_id = self.stage_in_progress

        # Try to edit task as portal user
        with self.assertRaises(AccessError):
            task.with_user(self.user_portal).write(
                {
                    "name": "Updated Task",
                }
            )

    def test_check_portal_fields_access(self):
        """Test _check_portal_fields_access method returns correct fields."""
        Task = self.env["project.task"]
        allowed_fields = Task._check_portal_fields_access()

        # Check that the method returns expected fields
        self.assertIsInstance(allowed_fields, list)
        self.assertIn("name", allowed_fields)
        self.assertIn("description", allowed_fields)
        self.assertIn("date_deadline", allowed_fields)
        self.assertEqual(len(allowed_fields), 3)

    def test_check_portal_edit_access_allowed(self):
        """Test check_portal_edit_access when access is allowed."""
        # Create task as portal user
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .create(
                {
                    "name": "Portal Task",
                    "description": "Task created by portal user",
                    "project_id": self.project.id,
                }
            )
        )

        # Check that portal user has edit access to their own task
        self.assertTrue(task.with_user(self.user_portal).check_portal_edit_access())

    def test_check_portal_edit_access_denied_no_portal_stage(self):
        """Test check_portal_edit_access denied when project has no portal stage."""
        # Create task as portal user
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .create(
                {
                    "name": "Portal Task",
                    "description": "Task created by portal user",
                    "project_id": self.project.id,
                }
            )
        )

        # Remove portal stage
        self.project.portal_stage_id = False

        # Check that portal user has no edit access
        self.assertFalse(task.with_user(self.user_portal).check_portal_edit_access())

    def test_check_portal_edit_access_denied_wrong_stage(self):
        """Test check_portal_edit_access denied when task is in wrong stage."""
        # Create task as portal user
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .create(
                {
                    "name": "Portal Task",
                    "description": "Task created by portal user",
                    "project_id": self.project.id,
                }
            )
        )

        # Move task to different stage
        task.sudo().stage_id = self.stage_in_progress

        # Check that portal user has no edit access
        self.assertFalse(task.with_user(self.user_portal).check_portal_edit_access())

    def test_check_portal_edit_access_denied_not_creator(self):
        """Test check_portal_edit_access denied when user is not the creator."""
        # Create task as admin
        task = self.env["project.task"].create(
            {
                "name": "Admin Task",
                "description": "Task created by admin",
                "project_id": self.project.id,
                "stage_id": self.stage_backlog.id,
            }
        )

        # Check that portal user has no edit access to admin's task
        self.assertFalse(
            task.with_user(self.user_portal).sudo().check_portal_edit_access()
        )

    def test_create_task_as_portal_clears_assignees(self):
        """Test that creating a task as portal user clears user_ids."""
        admin_user = self.env.ref("base.user_admin")
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .create(
                {
                    "name": "Portal Task",
                    "description": "Task created by portal user",
                    "project_id": self.project.id,
                    "user_ids": [(6, 0, [admin_user.id])],
                }
            )
        )

        self.assertFalse(task.user_ids)

    def test_create_task_as_internal_user_keeps_assignees(self):
        """Test that creating a task as internal user keeps user_ids."""
        admin_user = self.env.ref("base.user_admin")
        # Create task as internal user with user_ids
        task = self.env["project.task"].create(
            {
                "name": "Admin Task",
                "description": "Task created by admin",
                "project_id": self.project.id,
                "user_ids": [(6, 0, [admin_user.id])],
            }
        )

        # Check that user_ids is preserved
        self.assertTrue(task.user_ids)
        self.assertIn(admin_user, task.user_ids)
