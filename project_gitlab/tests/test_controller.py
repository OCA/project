# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os

from odoo.tests import tagged

from odoo.addons.project_git.tests.common import TEST_TOKEN, ProjectGitControllerCase


@tagged("post_install", "-at_install")
class TestGitlabWebhookController(ProjectGitControllerCase):
    """Real HTTP requests with the GitLab authorization scheme: the
    webhook token sent verbatim in the X-Gitlab-Token header."""

    RES_DIR = os.path.join(os.path.dirname(__file__), "res")

    def test_gitlab_wrong_token_is_rejected(self):
        jobs_before = self._job_count("_process_commit_push")
        result = self._post_webhook(
            self._load_payload("gitlab_push.json"),
            headers={
                "X-Gitlab-Event": "Push Hook",
                "X-Gitlab-Token": "not-the-right-token",
            },
        )
        self.assertIs(result, False)
        self.assertEqual(self._job_count("_process_commit_push"), jobs_before)

    def test_gitlab_valid_token_enqueues_job(self):
        jobs_before = self._job_count("_process_commit_push")
        self._post_webhook(
            self._load_payload("gitlab_push.json"),
            headers={"X-Gitlab-Event": "Push Hook", "X-Gitlab-Token": TEST_TOKEN},
        )
        self.assertEqual(self._job_count("_process_commit_push"), jobs_before + 1)

    def test_insecure_default_token_rejects_requests(self):
        # The demo default "token" is publicly known: a webhook sending
        # the matching header must be rejected anyway
        self.config.set_param("project_git.authorization_token", "token")
        jobs_before = self._job_count("_process_commit_push")
        result = self._post_webhook(
            self._load_payload("gitlab_push.json"),
            headers={"X-Gitlab-Event": "Push Hook", "X-Gitlab-Token": "token"},
        )
        self.assertIs(result, False)
        self.assertEqual(self._job_count("_process_commit_push"), jobs_before)

    def test_gitlab_event_without_handler_is_skipped(self):
        # Authorized event kinds without a _process_* handler (e.g. note
        # events) are acknowledged without enqueueing anything
        jobs_total_before = self.env["queue.job"].sudo().search_count([])
        result = self._post_webhook(
            {"object_kind": "note", "project": {}},
            headers={"X-Gitlab-Event": "Note Hook", "X-Gitlab-Token": TEST_TOKEN},
        )
        self.assertIs(result, True)
        self.assertEqual(
            self.env["queue.job"].sudo().search_count([]), jobs_total_before
        )
