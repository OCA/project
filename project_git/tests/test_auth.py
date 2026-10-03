# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError

from .common import ProjectGitCase


class TestGitAuth(ProjectGitCase):
    """Outbound token sysparam handling shared by the platform bridges."""

    def test_get_token_param(self):
        GitAuth = self.env["project.git.auth"]
        set_param = self.env["ir.config_parameter"].sudo().set_param
        # Missing sysparam
        with self.assertRaises(UserError):
            GitAuth._get_token_param("project_git.test.token")
        # Insecure demo default: rejected like a missing token
        set_param("project_git.test.token", "token")
        with self.assertRaises(UserError):
            GitAuth._get_token_param("project_git.test.token")
        # Real token: returned as-is
        set_param("project_git.test.token", "s3cr3t-t0k3n")
        self.assertEqual(
            GitAuth._get_token_param("project_git.test.token"), "s3cr3t-t0k3n"
        )
