# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.webhook_gitlab.models.git_event import DEFAULT_TASK_NAME_MATCH_REGEX

from .common import GITHUB_REPO_URL, GITLAB_REPO_URL, WebhookGitlabCase


class TestTaskMatching(WebhookGitlabCase):
    """Platform-agnostic tests for the task matching logic and its
    configuration (no webhook payload involved)."""

    def test_task_name_match_regex_param_seeded_but_never_overwritten(self):
        # The pattern regex sysparam is seeded on install/update so that
        # users find it ready to customize; an existing (possibly
        # customized) value is never overwritten
        config = self.env["ir.config_parameter"].sudo()
        config.search([("key", "=", "webhook_gitlab.task_name_match_regex")]).unlink()
        self.git_event._init_task_name_match_regex_param()
        self.assertEqual(
            config.get_param("webhook_gitlab.task_name_match_regex"),
            DEFAULT_TASK_NAME_MATCH_REGEX,
        )
        config.set_param("webhook_gitlab.task_name_match_regex", r"CUSTOM-\d+")
        self.git_event._init_task_name_match_regex_param()
        self.assertEqual(
            config.get_param("webhook_gitlab.task_name_match_regex"), r"CUSTOM-\d+"
        )

    def test_invalid_pattern_regex_falls_back_to_default(self):
        # A broken custom regex must not kill the webhook processing:
        # the matching falls back to the default pattern with a warning
        self.env["ir.config_parameter"].sudo().set_param(
            "webhook_gitlab.task_name_match_regex", "[invalid"
        )
        with self.assertLogs(
            "odoo.addons.webhook_gitlab.models.git_event", level="WARNING"
        ):
            matching_tasks = self.git_event._find_matching_tasks(
                projects=self.gitlab_project, pattern_text="GL-100 fix the export"
            )
        self.assertEqual(matching_tasks, self.gl_task_100)

    def test_task_id_reference_to_missing_task_is_ignored(self):
        # Outside PR/MR titles (which warn on the platform), a broken
        # explicit reference is silently skipped
        missing_id = (
            self.env["project.task"].search([], order="id desc", limit=1).id + 1000
        )
        matching_tasks = self.git_event._find_matching_tasks(
            projects=self.gitlab_project, pattern_text=f"tid#{missing_id} quick fix"
        )
        self.assertFalse(matching_tasks)

    def test_repository_matching_by_dev_project_url(self):
        # git_dev_project_url is an alternative mapping surface,
        # equivalent to git_project_url for repository matching
        dev_project = self.env["project.project"].create(
            {
                "name": "Dev Mirror Repo",
                "git_dev_project_url": "https://gitlab.example.com/acme/demo-dev-repo",
            }
        )
        repository_projects = self.git_event._get_related_projects_by_url(
            event={
                "repository_url": "https://gitlab.example.com/acme/demo-dev-repo.git"
            }
        )
        self.assertEqual(repository_projects, dev_project)

    def test_repository_matching_handles_git_suffix_variants(self):
        # gitlab_project is stored with the ".git" suffix, github_project
        # without: each must match the event URL spelled the other way
        repository_projects = self.git_event._get_related_projects_by_url(
            event={"repository_url": GITLAB_REPO_URL}
        )
        self.assertEqual(repository_projects, self.gitlab_project)
        repository_projects = self.git_event._get_related_projects_by_url(
            event={"repository_url": f"{GITHUB_REPO_URL}.git"}
        )
        self.assertEqual(repository_projects, self.github_project)

    def test_task_name_search_is_case_insensitive(self):
        # The extracted key is searched in the task names ignoring case,
        # as a task naming tolerance (the extraction stays strict)
        lowercase_task = self.env["project.task"].create(
            {
                "name": "gl-140 lowercase named task",
                "project_id": self.gitlab_project.id,
            }
        )
        matching_tasks = self.git_event._find_matching_tasks(
            projects=self.gitlab_project, pattern_text="GL-140 fix the export"
        )
        self.assertEqual(matching_tasks, lowercase_task)
