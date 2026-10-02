# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase, new_test_user, users


class TestProjectAdministratorRestrictedVisibility(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

    def _create_defaults(self):
        """Define default field values"""
        self.env["ir.default"].sudo().create(
            {
                "field_id": self.env.ref(
                    "project.field_project_project__privacy_visibility"
                ).id,
                "json_value": '"followers"',
                "user_id": self.env.user.id,
            }
        )

    @users("restricted-project-admin", "project-admin")
    def test_create_new_project(self):
        """'Restricted project administrator' can create
        projects like a 'Project administrator'.
        """
        self._create_defaults()
        project = self.env["project.project"].create({"name": "Another project"})
        self.assertEqual(project.privacy_visibility, "followers")
        project.write({"name": "Another test project"})
        project.unlink()

    @users("restricted-project-admin", "project-user")
    def test_cant_see_restricted_projects(self):
        """'Restricted project administrator' has the same project restriction
        as the 'Project user'.
        """
        all_project = self.env["project.project"].search([])
        self.assertNotIn(self.restricted_project, all_project)

    @users("project-admin")
    def test_can_see_all_projects(self):
        """'Full project administrator' can see all projects."""
        all_project = self.env["project.project"].search([])
        self.assertIn(self.restricted_project, all_project)
