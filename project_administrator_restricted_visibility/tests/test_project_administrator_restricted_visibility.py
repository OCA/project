# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase, new_test_user, users


class TestProjectAdministratorRestrictedVisibility(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
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
                "message_partner_ids": [(6, 0, cls.user_admin.ids)],
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
        """'Restricted project administrator' has the same project restriction
        as the 'Project user'.
        """
        all_project = self.env["project.project"].search([])
        self.assertNotIn(self.restricted_project, all_project)

    @users("restricted-project-admin")
    def test_can_manage_own_project(self):
        """A restricted administrator can manage their own project."""
        project = self.env["project.project"].browse(self.own_project.id)
        self.assertTrue(project.exists())
        project.write({"name": "Updated own project"})
        project.unlink()
