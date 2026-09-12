from odoo import Command

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.mail.tests.common import mail_new_test_user


class TestProjectVisibility(BaseCommon):
    @classmethod
    def setUpClass(cls):
        """Set up the class with initial data for tests."""
        super().setUpClass()
        cls.ProjectObj = cls.env["project.project"]
        cls.GroupObj = cls.env["res.groups"]
        cls.project_group_user = mail_new_test_user(
            cls.env,
            login="projectgroupuser",
            name="Project Group User",
            email="projectgroupuser@example.com",
            company_id=cls.env.company.id,
            groups="base.group_user",
        )
        cls.group1 = cls.GroupObj.create({"name": "Test Group 1"})
        cls.group2 = cls.GroupObj.create({"name": "Test Group 2"})
        cls.project = cls.ProjectObj.create(
            {"name": "Test Project", "privacy_visibility": "portal"}
        )
        cls.restricted_project = cls.ProjectObj.create(
            {
                "name": "Restricted Project",
                "privacy_visibility": "followers",
                "group_ids": [Command.set([cls.group1.id])],
            }
        )

    def test_01_group_ids_visibility(self):
        """Test the visibility of group_ids based on project privacy settings."""
        self.assertFalse(
            self.project.group_ids,
            "group_ids should not be set when visibility is 'portal'",
        )
        self.assertEqual(
            self.project.privacy_visibility,
            "portal",
            "privacy_visibility should be 'portal' initially",
        )

        self.project.write(
            {
                "privacy_visibility": "followers",
                "group_ids": [Command.set([self.group1.id, self.group2.id])],
            }
        )
        self.assertEqual(
            self.project.privacy_visibility,
            "followers",
            "privacy_visibility should be 'followers' after update",
        )
        self.assertTrue(
            self.project.group_ids,
            "group_ids should be set when visibility is 'followers'",
        )
        self.assertEqual(
            len(self.project.group_ids), 2, "There should be two groups assigned"
        )

        self.project.write(
            {
                "privacy_visibility": "employees",
            }
        )
        self.assertEqual(
            self.project.privacy_visibility,
            "employees",
            "privacy_visibility should be 'employees' after update",
        )

    def test_02_access_rights(self):
        """Test the access rights of users based on group membership."""
        self.assertEqual(
            self.restricted_project.privacy_visibility,
            "followers",
            "privacy_visibility should be 'followers' initially",
        )

        self.project_group_user.write({"group_ids": [Command.set([self.group2.id])]})
        self.assertNotIn(
            self.project_group_user,
            self.restricted_project.sudo().group_ids.all_user_ids,
            "User should not have access",
        )

        self.project_group_user.write({"group_ids": [Command.set([self.group1.id])]})
        self.assertIn(
            self.project_group_user,
            self.restricted_project.sudo().group_ids.all_user_ids,
            "User should have access",
        )

        self.restricted_project.write(
            {
                "privacy_visibility": "employees",
            }
        )
        self.assertEqual(
            self.restricted_project.privacy_visibility,
            "employees",
            "privacy_visibility should be 'employees' after update",
        )

    def test_03_invited_users_group_access(self):
        """Group members get access on 'invited_users' projects."""
        invited_project = self.ProjectObj.create(
            {
                "name": "Invited Users Project",
                "privacy_visibility": "invited_users",
                "group_ids": [Command.set([self.group1.id])],
            }
        )
        self.project_group_user.write({"group_ids": [Command.link(self.group2.id)]})
        self.assertNotIn(
            invited_project,
            self.ProjectObj.with_user(self.project_group_user).search(
                [("id", "=", invited_project.id)]
            ),
            "User outside the project groups should not see the project",
        )

        self.project_group_user.write(
            {
                "group_ids": [
                    Command.unlink(self.group2.id),
                    Command.link(self.group1.id),
                ]
            }
        )
        self.assertIn(
            invited_project,
            self.ProjectObj.with_user(self.project_group_user).search(
                [("id", "=", invited_project.id)]
            ),
            "User in a project group should see the 'invited_users' project",
        )
