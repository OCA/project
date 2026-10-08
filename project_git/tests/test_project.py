# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import ProjectGitCase


class TestProjectGitHelpers(ProjectGitCase):
    """Platform-agnostic project.project helpers of the webhook
    deployment flow (the deployments themselves are covered by the
    bridge test suites)."""

    def test_git_project_path(self):
        Project = self.env["project.project"]
        self.assertEqual(
            Project._git_project_path("https://gitlab.example.com/acme/demo-repo"),
            "acme/demo-repo",
        )
        # Trailing .git and slashes are tolerated
        self.assertEqual(
            Project._git_project_path("https://gitlab.example.com/acme/demo-repo.git/"),
            "acme/demo-repo",
        )

    def test_get_webhook_url(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "web.base.url", "https://odoo.example.com/"
        )
        self.assertEqual(
            self.env["project.project"]._get_webhook_url(),
            "https://odoo.example.com/project_git/webhook/",
        )
