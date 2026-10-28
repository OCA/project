# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import AccessError
from odoo.tests.common import new_test_user, users

from odoo.addons.base.tests.common import BaseCommon


class TestProjectAdministratorRestrictedVisibility(BaseCommon):
    _test_user_groups = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_obj = cls.env["project.project"]
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.user_user_padmin = new_test_user(
            cls.env,
            login="project-user",
            groups="project.group_project_user",
        )
        cls.user_restrcited_padmin = new_test_user(
            cls.env,
            login="restricted-project-admin",
            groups="project.group_project_manager",
        )
        cls.user_full_padmin = new_test_user(
            cls.env,
            login="project-admin",
            groups="project_administrator_restricted_visibility.group_full_project_manager",
        )
        cls.restricted_project = cls.env["project.project"].create(
            {
                "name": "Restricted project",
                "privacy_visibility": "followers",
                "user_id": cls.user_admin.id,
                "message_partner_ids": [(6, 0, cls.user_admin.partner_id.ids)],
            }
        )
        cls.restricted_task = cls.env["project.task"].create(
            {
                "name": "Private task",
                "project_id": cls.restricted_project.id,
                "user_ids": [(6, 0, cls.user_admin.ids)],
            }
        )
        cls.own_project = cls.env["project.project"].create(
            {
                "name": "Own project",
                "privacy_visibility": "followers",
                "user_id": cls.user_restrcited_padmin.id,
                # Only admin follows it: visibility comes from ownership.
                "message_partner_ids": [(6, 0, cls.user_admin.partner_id.ids)],
            }
        )
        cls.public_project = cls.env["project.project"].create(
            {
                "name": "Public project",
                "privacy_visibility": "employees",
                "user_id": cls.user_admin.id,
            }
        )
        cls.public_task = cls.env["project.task"].create(
            {
                "name": "Public task",
                "project_id": cls.public_project.id,
                "user_ids": [(6, 0, cls.user_admin.ids)],
            }
        )

    @users("restricted-project-admin", "project-admin")
    def test_create_new_project(self):
        """'Restricted project administrator' can create
        projects like a 'Project administrator'.
        """
        project = self.project_obj.create(
            {
                "name": "Another project",
                "privacy_visibility": "invited_users",
                "user_id": self.env.user.id,
            }
        )
        self.assertIn(project, self.project_obj.search([]))
        project.write({"name": "Updated project"})
        project.unlink()

    @users("restricted-project-admin", "project-user")
    def test_cant_see_restricted_projects(self):
        """'Restricted project administrator' has the same project and task restrictions
        as the 'Project user'.
        """
        all_project = self.env["project.project"].search([])
        self.assertNotIn(self.restricted_project, all_project)
        self.assertIn(self.public_project, all_project)
        all_task = self.env["project.task"].search([])
        self.assertNotIn(self.restricted_task, all_task)
        self.assertIn(self.public_task, all_task)

    @users("restricted-project-admin")
    def test_cant_manage_restricted_projects(self):
        """A restricted administrator can't access projects and tasks it can't see."""
        with self.assertRaises(AccessError):
            self.env["project.project"].browse(self.restricted_project.id).read(
                ["name"]
            )
        with self.assertRaises(AccessError):
            self.env["project.task"].browse(self.restricted_task.id).write(
                {"name": "Updated private task"}
            )

    @users("restricted-project-admin")
    def test_can_manage_visible_projects(self):
        """A restricted administrator keeps the administrator rights on the
        projects and tasks it can see."""
        project = self.env["project.project"].browse(self.public_project.id)
        project.write({"name": "Updated public project"})
        task = self.env["project.task"].create(
            {"name": "New task", "project_id": project.id}
        )
        task.write({"name": "Updated task"})
        self.env["project.task"].browse(self.public_task.id).unlink()
        project.unlink()

    @users("restricted-project-admin")
    def test_can_manage_own_project(self):
        """A restricted administrator can manage their own project."""
        project = self.env["project.project"].browse(self.own_project.id)
        self.assertTrue(project.exists())
        project.write({"name": "Updated own project"})
        project.unlink()

    @users("project-admin")
    def test_full_administrator_sees_all(self):
        """A full administrator sees every project and task."""
        self.assertIn(self.restricted_project, self.env["project.project"].search([]))
        self.assertIn(self.restricted_task, self.env["project.task"].search([]))
        self.env["project.project"].browse(self.restricted_project.id).write(
            {"name": "Updated restricted project"}
        )
