# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.webhook_gitlab.models.git_event import DEFAULT_TASK_NAME_MATCH_REGEX

from .common import WebhookGitlabCase


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
