# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError

from odoo.addons.project.tests.test_access_rights import TestAccessRights


class TestPortalInternalAccess(TestAccessRights):
    """
    Tests for the `portal_internal` visibility mode:
    - Portal user may read only when subscribed
    - Portal user cannot write/create/unlink projects and tasks
    """

    @classmethod
    def setUpClass(cls):
        super(TestPortalInternalAccess, cls).setUpClass()
        # Switch the demo project to the new portal_internal mode
        cls.project_pigs.privacy_visibility = "portal_internal"
        cls.env.flush_all()

    def test_project_no_read_without_subscription(self):
        """Portal user cannot read project before subscribing"""
        with self.assertRaises(AccessError):
            _ = self.project_pigs.with_user(self.portal).name

    def test_project_read_with_subscription(self):
        """Portal user reads project after subscribing"""
        self.project_pigs.message_subscribe([self.portal.partner_id.id])
        _ = self.project_pigs.with_user(self.portal).name

    def test_project_write_unlink_forbidden(self):
        """Portal user cannot write or unlink at any time"""
        # write
        with self.assertRaises(AccessError):
            self.project_pigs.with_user(self.portal).write({"name": "New Name"})
        # unlink
        self.project_pigs.message_subscribe([self.portal.partner_id.id])
        with self.assertRaises(AccessError):
            self.project_pigs.with_user(self.portal).unlink()

    def test_task_no_read_without_subscription(self):
        """Portal user cannot read task before subscribing"""
        with self.assertRaises(AccessError):
            _ = self.task.with_user(self.portal).name

    def test_task_read_with_subscription(self):
        """Portal user reads task after subscribing"""
        self.project_pigs.message_subscribe([self.portal.partner_id.id])
        self.task.flush_model()
        _ = self.task.with_user(self.portal).name

    def test_task_write_forbidden(self):
        """Portal user cannot write tasks"""
        self.project_pigs.message_subscribe([self.portal.partner_id.id])
        self.task.flush_model()
        with self.assertRaises(AccessError):
            self.task.with_user(self.portal).write({"name": "X"})

    def test_task_create_forbidden(self):
        """Portal user cannot create tasks"""
        self.project_pigs.message_subscribe([self.portal.partner_id.id])
        with self.assertRaises(AccessError):
            self.env["project.task"].with_user(self.portal).create(
                {
                    "name": "ShouldFail",
                    "project_id": self.project_pigs.id,
                }
            )

    def test_task_unlink_forbidden(self):
        """Portal user cannot unlink tasks"""
        self.project_pigs.message_subscribe([self.portal.partner_id.id])
        self.task.flush_model()
        with self.assertRaises(AccessError):
            self.task.with_user(self.portal).unlink()

    def test_internal_user_project_no_read_without_subscription(self):
        """Internal user cannot read portal_internal project without subscription"""
        with self.assertRaises(AccessError):
            _ = self.project_pigs.with_user(self.user).name

    def test_internal_user_project_read_with_subscription(self):
        """Internal user can read portal_internal project after subscribing"""
        self.project_pigs.message_subscribe([self.user.partner_id.id])
        self.env["project.project"].flush_model()
        _ = self.project_pigs.with_user(self.user).name

    def test_internal_user_task_no_read_without_subscription(self):
        """Internal user cannot read tasks of portal_internal project without subscription"""
        with self.assertRaises(AccessError):
            _ = self.task.with_user(self.user).name

    def test_internal_user_task_read_with_subscription(self):
        """Internal user can read tasks of portal_internal project after subscribing"""
        self.project_pigs.message_subscribe([self.user.partner_id.id])
        self.task.flush_model()
        _ = self.task.with_user(self.user).name

    def test_internal_user_task_assigned_user_can_read(self):
        """Internal user can read task if assigned in user_ids"""
        # Unsubscribe to ensure only assignment grants access
        self.project_pigs.message_unsubscribe([self.user.partner_id.id])
        # Assign user to task
        self.task.write({"user_ids": [(4, self.user.id)]})
        self.task.flush_model()
        _ = self.task.with_user(self.user).name
