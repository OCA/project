# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta
from unittest.mock import patch

from odoo.fields import Date
from odoo.http import Request
from odoo.tests import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserPortal
from odoo.addons.project.tests.test_access_rights import TestProjectPortalCommon

# Import controller
from odoo.addons.project_task_create_portal.controllers.portal import (
    ProjectCustomerNewPortal,
)


@tagged("post_install", "-at_install")
class TestPortalController(TestProjectPortalCommon, HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super(TestPortalController, cls).setUpClass()

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
        cls.user_portal.password = cls.user_portal.login

        # Set portal task creation stage
        cls.project.portal_stage_id = cls.stage_backlog

        # Set portal allowed users
        cls.project.portal_user_ids = cls.user_portal

        cls.controller = ProjectCustomerNewPortal()

    def test_validate_task_fields_all_valid(self):
        """Test _validate_task_fields with all valid fields."""
        data = {
            "name": "Test Task",
            "description": "Test Description",
            "date_deadline": Date.to_string(date.today() + timedelta(days=1)),
        }
        error, error_message = self.controller._validate_task_fields(data)

        self.assertFalse(error)
        self.assertFalse(error_message)

    def test_validate_task_fields_missing_name(self):
        """Test _validate_task_fields with missing name."""
        data = {
            "description": "Test Description",
        }
        error, error_message = self.controller._validate_task_fields(data)

        self.assertIn("name", error)
        self.assertEqual(error["name"], "missing")

    def test_validate_task_fields_missing_description(self):
        """Test _validate_task_fields with missing description."""
        data = {
            "name": "Test Task",
        }
        error, error_message = self.controller._validate_task_fields(data)

        self.assertIn("description", error)
        self.assertEqual(error["description"], "missing")

    def test_validate_task_fields_deadline_in_past(self):
        """Test _validate_task_fields with deadline in the past."""
        data = {
            "name": "Test Task",
            "description": "Test Description",
            "date_deadline": Date.to_string(date.today() - timedelta(days=1)),
        }
        error, error_message = self.controller._validate_task_fields(data)

        self.assertIn("date_deadline", error)
        self.assertEqual(error["date_deadline"], "invalid")
        self.assertIn("Deadline is in the past", error_message)

    def test_validate_task_fields_no_deadline(self):
        """Test _validate_task_fields without deadline (optional field)."""
        data = {
            "name": "Test Task",
            "description": "Test Description",
        }
        error, error_message = self.controller._validate_task_fields(data)

        self.assertFalse(error)
        self.assertFalse(error_message)

    def test_prepare_task_values_mandatory_only(self):
        """Test _prepare_task_values with mandatory fields only."""
        data = {
            "name": "Test Task",
            "description": "Test Description",
        }
        values = self.controller._prepare_task_values(data)

        self.assertEqual(values["name"], "Test Task")
        self.assertEqual(values["description"], "Test Description")
        self.assertNotIn("date_deadline", values)

    def test_prepare_task_values_with_deadline(self):
        """Test _prepare_task_values with deadline."""
        deadline = Date.to_string(date.today() + timedelta(days=1))
        data = {
            "name": "Test Task",
            "description": "Test Description",
            "date_deadline": deadline,
        }
        values = self.controller._prepare_task_values(data)

        self.assertEqual(values["name"], "Test Task")
        self.assertEqual(values["description"], "Test Description")
        self.assertEqual(values["date_deadline"], deadline)

    def test_prepare_task_values_ignores_extra_fields(self):
        """Test _prepare_task_values ignores fields not in allowed list."""
        data = {
            "name": "Test Task",
            "description": "Test Description",
            "priority": "1",
            "user_ids": [(6, 0, [1])],
        }
        values = self.controller._prepare_task_values(data)

        self.assertEqual(values["name"], "Test Task")
        self.assertEqual(values["description"], "Test Description")

    def test_task_action_page_view_values(self):
        """Test _task_action_page_view_values returns correct structure."""
        with patch.object(
            self.controller,
            "_prepare_portal_layout_values",
            return_value={"base": "values"},
        ):
            values = self.controller._task_action_page_view_values(self.project)

            self.assertIn("project", values)
            self.assertEqual(values["project"], self.project)
            self.assertIn("error", values)
            self.assertEqual(values["error"], {})
            self.assertIn("error_message", values)
            self.assertEqual(values["error_message"], [])
            self.assertIn("base", values)

    def test_portal_project_create_task_get_request(self):
        """Test portal_project_create_task with GET request."""
        self.authenticate(self.user_portal.login, self.user_portal.login)
        response = self.url_open(
            f"/my/projects/{self.project.id}/task/new",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Project", response.content)

    def test_portal_project_create_task_post_valid(self):
        """Test portal_project_create_task with valid POST request."""
        self.authenticate(self.user_portal.login, self.user_portal.login)

        post_data = {
            "name": "Test Task from Portal",
            "description": "Test Description from Portal",
            "date_deadline": Date.to_string(date.today() + timedelta(days=1)),
            "csrf_token": Request.csrf_token(self),
        }

        response = self.url_open(
            f"/my/projects/{self.project.id}/task/new",
            data=post_data,
        )

        # Should redirect to task view
        self.assertEqual(response.status_code, 200)

        # Check task was created
        task = (
            self.env["project.task"]
            .sudo()
            .search([("name", "=", "Test Task from Portal")])
        )
        self.assertTrue(task)
        self.assertEqual(task.project_id, self.project)
        self.assertEqual(task.stage_id, self.stage_backlog)
        self.assertEqual(task.create_uid, self.user_portal)

    def test_portal_project_create_task_post_invalid(self):
        """Test portal_project_create_task with invalid POST request."""
        self.authenticate(self.user_portal.login, self.user_portal.login)

        post_data = {
            "name": "",  # Missing name
            "description": "Test Description",
            "csrf_token": Request.csrf_token(self),
        }

        response = self.url_open(
            f"/my/projects/{self.project.id}/task/new",
            data=post_data,
        )

        # Should stay on the form with errors
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Project", response.content)

    def test_portal_project_create_task_project_not_found(self):
        """Test portal_project_create_task with non-existent project."""
        self.authenticate(self.user_portal.login, self.user_portal.login)

        response = self.url_open("/my/projects/99999/task/new")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Project not found!", response.text)

    def test_portal_project_create_task_not_allowed(self):
        """Test portal_project_create_task when not allowed."""
        self.authenticate(self.user_portal.login, self.user_portal.login)

        # Remove portal stage
        self.project.portal_stage_id = False

        response = self.url_open(f"/my/projects/{self.project.id}/task/new")
        self.assertIn(
            "You are not allowed to create tasks in this project.", response.text
        )
        self.assertEqual(response.status_code, 403)

    def test_portal_project_edit_task_get_request(self):
        """Test portal_project_edit_task with GET request."""
        self.authenticate(self.user_portal.login, self.user_portal.login)

        # Create task
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .create(
                {
                    "name": "Portal Task",
                    "description": "Test Description",
                    "project_id": self.project.id,
                }
            )
        )

        response = self.url_open(f"/my/projects/{self.project.id}/task/{task.id}/edit")

        self.assertEqual(response.status_code, 200)

    def test_portal_project_edit_task_post_valid(self):
        """Test portal_project_edit_task with valid POST request."""
        self.authenticate(self.user_portal.login, self.user_portal.login)

        # Create task
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .create(
                {
                    "name": "Portal Task",
                    "description": "Test Description",
                    "project_id": self.project.id,
                }
            )
        )

        post_data = {
            "name": "Updated Portal Task",
            "description": "Updated Description",
            "date_deadline": Date.to_string(date.today() + timedelta(days=1)),
            "csrf_token": Request.csrf_token(self),
        }

        response = self.url_open(
            f"/my/projects/{self.project.id}/task/{task.id}/edit",
            data=post_data,
        )

        # Should redirect to task view
        self.assertEqual(response.status_code, 200)

        # Check task was updated
        task = self.env["project.task"].sudo().browse(task.id)
        self.assertEqual(task.name, "Updated Portal Task")
        self.assertIn("Updated Description", task.description)

    def test_portal_project_edit_task_post_invalid(self):
        """Test portal_project_edit_task with invalid POST request."""
        self.authenticate(self.user_portal.login, self.user_portal.login)

        # Create task
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .create(
                {
                    "name": "Portal Task",
                    "description": "Test Description",
                    "project_id": self.project.id,
                }
            )
        )

        post_data = {
            "name": "",  # Missing name
            "description": "Test Description",
            "csrf_token": Request.csrf_token(self),
        }

        response = self.url_open(
            f"/my/projects/{self.project.id}/task/{task.id}/edit",
            data=post_data,
        )

        # Should stay on the form with errors
        self.assertEqual(response.status_code, 200)

    def test_portal_project_edit_task_not_found(self):
        """Test portal_project_edit_task with non-existent task."""
        self.authenticate(self.user_portal.login, self.user_portal.login)

        response = self.url_open(f"/my/projects/{self.project.id}/task/99999/edit")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Task not found!", response.text)

    def test_portal_project_edit_task_not_allowed(self):
        """Test portal_project_edit_task when not allowed."""
        self.authenticate(self.user_portal.login, self.user_portal.login)

        # Create task
        task = (
            self.env["project.task"]
            .with_user(self.user_portal)
            .create(
                {
                    "name": "Portal Task",
                    "description": "Test Description",
                    "project_id": self.project.id,
                }
            )
        )

        # Remove portal stage
        self.project.portal_stage_id = False

        response = self.url_open(f"/my/projects/{self.project.id}/task/{task.id}/edit")
        self.assertEqual(response.status_code, 403)
        self.assertIn("You are not allowed to edit this task.", response.text)

    def test_portal_project_edit_task_wrong_project(self):
        """Test portal_project_edit_task with task from different project."""
        self.authenticate(self.user_portal.login, self.user_portal.login)

        # Create another project
        other_project = self.env["project.project"].create(
            {
                "name": "Other Project",
            }
        )

        # Create task in other project
        task = self.env["project.task"].create(
            {
                "name": "Other Task",
                "description": "Test Description",
                "project_id": other_project.id,
            }
        )

        response = self.url_open(f"/my/projects/{self.project.id}/task/{task.id}/edit")
        self.assertEqual(response.status_code, 400)
