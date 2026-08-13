# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from unittest.mock import MagicMock, patch

from gitlab.exceptions import GitlabJobRetryError

from odoo.exceptions import UserError

from odoo.addons.webhook_gitlab.models.git_auth import GitAuth

from .common import GITLAB_REPO_URL, WebhookGitlabCase

ODOO_BASE_URL = "https://odoo.example.com"
WEBHOOK_TOKEN = "webhook-secret-token"
GITHUB_COM_REPO_URL = "https://github.com/acme/webhook-demo"


class TestProjectWebhookDeploy(WebhookGitlabCase):
    """Webhook deployment on the GitLab/GitHub repo and Odoo.sh deploy job
    retry, both triggered from the Odoo project form."""

    def setUp(self):
        super().setUp()
        config = self.env["ir.config_parameter"].sudo()
        config.set_param("web.base.url", ODOO_BASE_URL)
        config.set_param("webhook_gitlab.authorization_token", WEBHOOK_TOKEN)
        self.expected_hook_url = f"{ODOO_BASE_URL}/webhook_gitlab/webhook/"
        # Platform detection is by host: the deploy runs against the GitHub
        # API only for github.com URLs (the fixture host is a GitLab one)
        self.githubcom_project = self.env["project.project"].create(
            {"name": "GitHub.com Repo", "git_project_url": GITHUB_COM_REPO_URL}
        )

    def _mock_gitlab_for_project(self, hooks=(), jobs=()):
        """Return (patcher, gitlab client mock) with hook/job fixtures
        installed on the mocked GitLab project."""
        client = MagicMock(name="gitlab_client")
        gitlab_project = client.projects.get.return_value
        gitlab_project.hooks.list.return_value = list(hooks)
        gitlab_project.jobs.list.return_value = list(jobs)
        patcher = patch.object(GitAuth, "_connect_gitlab", return_value=client)
        return patcher, client

    def _mock_github_for_project(self, hooks=()):
        """Return (patcher, github client mock) with hook fixtures
        installed on the mocked GitHub repository."""
        client = MagicMock(name="github_client")
        client.get_repo.return_value.get_hooks.return_value = list(hooks)
        patcher = patch.object(GitAuth, "_connect_github", return_value=client)
        return patcher, client

    @staticmethod
    def _hook_stub(url):
        hook = MagicMock(name="gitlab_hook")
        hook.url = url
        return hook

    @staticmethod
    def _github_hook_stub(url):
        hook = MagicMock(name="github_hook")
        hook.config = {"url": url, "content_type": "json"}
        return hook

    @staticmethod
    def _job_stub(name, created_at):
        job = MagicMock(name="gitlab_job")
        job.name = name
        job.created_at = created_at
        return job

    # ---- create_project_webhook ----

    def test_create_webhook_creates_hook_with_events(self):
        patcher, client = self._mock_gitlab_for_project()
        with patcher as connect_gitlab:
            self.gitlab_project.create_project_webhook()
        connect_gitlab.assert_called_once_with(url=f"{GITLAB_REPO_URL}.git")
        # Trailing .git is stripped from the API project path
        client.projects.get.assert_called_once_with("acme/demo-repo")
        client.projects.get.return_value.hooks.create.assert_called_once_with(
            {
                "url": self.expected_hook_url,
                "push_events": True,
                "merge_requests_events": True,
                "pipeline_events": True,
                "enable_ssl_verification": True,
                "token": WEBHOOK_TOKEN,
            }
        )

    def test_create_webhook_replaces_existing_hook(self):
        stale_hook = self._hook_stub(self.expected_hook_url)
        foreign_hook = self._hook_stub("https://ci.example.com/hook")
        patcher, client = self._mock_gitlab_for_project(
            hooks=[stale_hook, foreign_hook]
        )
        with patcher:
            self.gitlab_project.create_project_webhook()
        stale_hook.delete.assert_called_once_with()
        foreign_hook.delete.assert_not_called()
        client.projects.get.return_value.hooks.create.assert_called_once()

    def test_create_webhook_on_both_project_urls(self):
        self.gitlab_project.git_dev_project_url = f"{GITLAB_REPO_URL}-dev"
        patcher, client = self._mock_gitlab_for_project()
        with patcher:
            self.gitlab_project.create_project_webhook()
        self.assertEqual(
            [call.args for call in client.projects.get.call_args_list],
            [("acme/demo-repo",), ("acme/demo-repo-dev",)],
        )
        self.assertEqual(client.projects.get.return_value.hooks.create.call_count, 2)

    def test_create_webhook_without_url_does_nothing(self):
        self.gitlab_project.git_project_url = False
        patcher, _client = self._mock_gitlab_for_project()
        with patcher as connect_gitlab:
            self.gitlab_project.create_project_webhook()
        connect_gitlab.assert_not_called()

    def test_create_webhook_github_creates_hook_with_events(self):
        gitlab_patcher, _gitlab_client = self._mock_gitlab_for_project()
        github_patcher, github_client = self._mock_github_for_project()
        with gitlab_patcher as connect_gitlab, github_patcher:
            self.githubcom_project.create_project_webhook()
        # github.com URL: the GitHub API is used, not the GitLab one
        connect_gitlab.assert_not_called()
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

    # ---- retry_odoo_sh_deploy_job ----

    def test_retry_deploy_job_retries_latest(self):
        older_job = self._job_stub("odoo_sh_deploy", "2026-01-01T10:00:00Z")
        latest_job = self._job_stub("odoo_sh_deploy", "2026-02-01T10:00:00Z")
        other_job = self._job_stub("tests", "2026-03-01T10:00:00Z")
        latest_job.retry.return_value = {"web_url": f"{GITLAB_REPO_URL}/-/jobs/42"}
        patcher, _client = self._mock_gitlab_for_project(
            jobs=[older_job, latest_job, other_job]
        )
        with patcher:
            action = self.gitlab_project.retry_odoo_sh_deploy_job()
        older_job.retry.assert_not_called()
        other_job.retry.assert_not_called()
        self.assertEqual(
            action,
            {
                "type": "ir.actions.act_url",
                "url": f"{GITLAB_REPO_URL}/-/jobs/42",
                "target": "new",
            },
        )

    def test_retry_deploy_job_skips_github_url(self):
        # The CI job retry is GitLab-only: github.com URLs are skipped
        patcher, _client = self._mock_gitlab_for_project()
        with patcher as connect_gitlab:
            self.githubcom_project.retry_odoo_sh_deploy_job()
        connect_gitlab.assert_not_called()

    def test_retry_deploy_job_without_match_raises(self):
        patcher, _client = self._mock_gitlab_for_project(
            jobs=[self._job_stub("tests", "2026-01-01T10:00:00Z")]
        )
        with patcher, self.assertRaisesRegex(UserError, "No job odoo_sh_deploy"):
            self.gitlab_project.retry_odoo_sh_deploy_job()

    def test_retry_deploy_job_in_progress_raises(self):
        running_job = self._job_stub("odoo_sh_deploy", "2026-01-01T10:00:00Z")
        running_job.retry.side_effect = GitlabJobRetryError()
        patcher, _client = self._mock_gitlab_for_project(jobs=[running_job])
        with patcher, self.assertRaisesRegex(UserError, "cannot be retried"):
            self.gitlab_project.retry_odoo_sh_deploy_job()
