# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from unittest.mock import MagicMock, patch

from odoo.addons.project_github.models.project_git_auth import ProjectGitAuth

from .common import ProjectGithubCase

ODOO_BASE_URL = "https://odoo.example.com"
WEBHOOK_TOKEN = "webhook-secret-token"
GITHUB_COM_REPO_URL = "https://github.com/acme/webhook-demo"


class TestProjectWebhookDeploy(ProjectGithubCase):
    """Webhook deployment on the GitHub repo, triggered from the Odoo
    project form. Platform detection is by host: the deploy runs
    against the GitHub API for github.com URLs only (the shared
    github_project fixture points to a non-github.com host on
    purpose)."""

    def setUp(self):
        super().setUp()
        config = self.env["ir.config_parameter"].sudo()
        config.set_param("web.base.url", ODOO_BASE_URL)
        config.set_param("project_git.authorization_token", WEBHOOK_TOKEN)
        self.expected_hook_url = f"{ODOO_BASE_URL}/project_git/webhook/"
        self.githubcom_project = self.env["project.project"].create(
            {"name": "GitHub.com Repo", "git_project_url": GITHUB_COM_REPO_URL}
        )

    def _mock_github_for_project(self, hooks=()):
        """Return (patcher, github client mock) with hook fixtures
        installed on the mocked GitHub repository."""
        client = MagicMock(name="github_client")
        client.get_repo.return_value.get_hooks.return_value = list(hooks)
        patcher = patch.object(ProjectGitAuth, "_connect_github", return_value=client)
        return patcher, client

    @staticmethod
    def _github_hook_stub(url):
        hook = MagicMock(name="github_hook")
        hook.config = {"url": url, "content_type": "json"}
        return hook

    def test_create_webhook_github_creates_hook_with_events(self):
        patcher, github_client = self._mock_github_for_project()
        with patcher:
            self.githubcom_project.create_project_webhook()
        github_client.get_repo.assert_called_once_with("acme/webhook-demo")
        github_client.get_repo.return_value.create_hook.assert_called_once_with(
            name="web",
            config={
                "url": self.expected_hook_url,
                "content_type": "json",
                "secret": WEBHOOK_TOKEN,
                "insecure_ssl": "0",
            },
            events=["push", "pull_request"],
            active=True,
        )

    def test_create_webhook_github_replaces_existing_hook(self):
        stale_hook = self._github_hook_stub(self.expected_hook_url)
        foreign_hook = self._github_hook_stub("https://ci.example.com/hook")
        patcher, github_client = self._mock_github_for_project(
            hooks=[stale_hook, foreign_hook]
        )
        with patcher:
            self.githubcom_project.create_project_webhook()
        stale_hook.delete.assert_called_once_with()
        foreign_hook.delete.assert_not_called()
        github_client.get_repo.return_value.create_hook.assert_called_once()
