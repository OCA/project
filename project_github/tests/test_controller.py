# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json
import os
from hashlib import sha256
from hmac import HMAC

from odoo.tests import tagged

from odoo.addons.project_git.tests.common import TEST_TOKEN, ProjectGitControllerCase


@tagged("post_install", "-at_install")
class TestGithubWebhookController(ProjectGitControllerCase):
    """Real HTTP requests with the GitHub authorization scheme: the
    request body signed with the webhook secret (HMAC-SHA256)."""

    RES_DIR = os.path.join(os.path.dirname(__file__), "res")

    @staticmethod
    def _github_signature(payload, token=TEST_TOKEN):
        """Compute the X-Hub-Signature-256 header value the way GitHub
        does: HMAC-SHA256 of the raw request body with the shared token.
        The payload must be serialized exactly like _post_webhook does."""
        digest = HMAC(
            key=token.encode("utf-8"),
            msg=json.dumps(payload).encode("utf-8"),
            digestmod=sha256,
        ).hexdigest()
        return f"sha256={digest}"

    def test_github_valid_signature_enqueues_job(self):
        payload = self._load_payload("github_push.json")
        jobs_before = self._job_count("_process_commit_push_github")
        self._post_webhook(
            payload,
            headers={
                "X-GitHub-Event": "push",
                "X-Hub-Signature-256": self._github_signature(payload),
            },
        )
        self.assertEqual(
            self._job_count("_process_commit_push_github"), jobs_before + 1
        )

    def test_github_invalid_signature_is_rejected(self):
        jobs_before = self._job_count("_process_commit_push_github")
        result = self._post_webhook(
            self._load_payload("github_push.json"),
            headers={
                "X-GitHub-Event": "push",
                "X-Hub-Signature-256": f"sha256={'0' * 64}",
            },
        )
        self.assertIs(result, False)
        self.assertEqual(self._job_count("_process_commit_push_github"), jobs_before)

    def test_github_event_without_handler_is_skipped(self):
        # GitHub events are classified by their X-GitHub-Event header:
        # types without a _process_* handler (e.g. the ping event sent
        # on hook creation) are acknowledged without enqueueing anything
        payload = {"zen": "Design for failure.", "hook_id": 1, "repository": {}}
        jobs_total_before = self._job_count()
        result = self._post_webhook(
            payload,
            headers={
                "X-GitHub-Event": "ping",
                "X-Hub-Signature-256": self._github_signature(payload),
            },
        )
        self.assertIs(result, True)
        self.assertEqual(self._job_count(), jobs_total_before)
