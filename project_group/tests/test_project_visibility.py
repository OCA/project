from odoo import Command
from odoo.exceptions import AccessError

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.mail.tests.common import mail_new_test_user


class TestProjectVisibility(BaseCommon):
    # Run as superuser like before 20.0 (BaseCommon now uses a regular test user)
    _test_user_groups = None

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

    def test_03_ir_access_domains(self):
        """Users only reach 'followers' projects and tasks through a shared group."""
        task = self.env["project.task"].create(
            {"name": "Restricted Task", "project_id": self.restricted_project.id}
        )
        internal = self.project_group_user
        project_user = mail_new_test_user(
            self.env,
            login="projectgroupmember",
            name="Project Group Member",
            groups="project.group_project_user",
        )
        for user in (internal, project_user):
            user = user.with_user(user)
            self.assertFalse(
                self.restricted_project.with_user(user).search_count(
                    [("id", "=", self.restricted_project.id)]
                )
            )
            self.assertFalse(task.with_user(user).search_count([("id", "=", task.id)]))
        (internal | project_user).write({"group_ids": [Command.link(self.group1.id)]})
        # Tasks need no own access record: core 20.0 task rules check project access
        self.assertEqual(
            self.restricted_project.with_user(internal).search_count(
                [("id", "=", self.restricted_project.id)]
            ),
            1,
        )
        self.assertEqual(
            task.with_user(internal).search_count([("id", "=", task.id)]), 1
        )
        # project users may also edit the task, plain employees stay read-only
        task.with_user(project_user).write({"name": "Edited by project user"})
        self.assertEqual(task.name, "Edited by project user")
        with self.assertRaises(AccessError):
            task.with_user(internal).write({"name": "Not allowed"})
        with self.assertRaises(AccessError):
            self.restricted_project.with_user(internal).write({"name": "Nope"})
        # a project that does not list the group stays hidden
        self.restricted_project.group_ids = self.group2
        self.assertFalse(
            self.restricted_project.with_user(internal).search_count(
                [("id", "=", self.restricted_project.id)]
            )
        )
