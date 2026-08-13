# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json
import os
from hashlib import sha256
from hmac import HMAC

from odoo.tests import tagged
from odoo.tests.common import HttpCase

from .common import RES_DIR

TEST_TOKEN = "unit-test-webhook-secret"
WEBHOOK_URL = "/webhook_gitlab/webhook/"


@tagged("post_install", "-at_install")
class TestWebhookController(HttpCase):
    """Real HTTP requests against the webhook route, covering the layers
    that the state-based suite bypasses on purpose: the token
    authorization decorator and the event dispatch. Accepted events are
    only checked up to the queue job enqueueing (the processing itself
    is covered by the state-based suite)."""

    def setUp(self):
        super().setUp()
        self.config = self.env["ir.config_parameter"].sudo()
        self.config.set_param("webhook_gitlab.authorization_token", TEST_TOKEN)

    @staticmethod
    def _load_payload(name):
        with open(os.path.join(RES_DIR, name), encoding="utf-8") as payload_file:
            return json.load(payload_file)

    def _post_webhook(self, payload, headers=None):
        """POST the payload to the webhook route and return the JSON-RPC
        result (the return value of the controller)."""
        request_headers = {"Content-Type": "application/json"}
        request_headers.update(headers or {})
        response = self.url_open(
            WEBHOOK_URL, data=json.dumps(payload), headers=request_headers
        )
        response.raise_for_status()
        response_data = response.json()
        self.assertNotIn(
            "error", response_data, response_data.get("error", {}).get("data")
        )
        return response_data.get("result")

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

    def _job_count(self, method_name):
        return (
            self.env["queue.job"]
            .sudo()
            .search_count([("method_name", "=", method_name)])
        )

    def test_request_without_auth_headers_is_rejected(self):
        jobs_before = self._job_count("_process_commit_push")
        result = self._post_webhook(self._load_payload("gitlab_push.json"))
        self.assertIs(result, False)
        self.assertEqual(self._job_count("_process_commit_push"), jobs_before)

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

    def test_github_valid_signature_enqueues_job(self):
        payload = self._load_payload("github_push.json")
        jobs_before = self._job_count("_process_commit_push")
        self._post_webhook(
            payload,
            headers={"X-Hub-Signature-256": self._github_signature(payload)},
        )
        self.assertEqual(self._job_count("_process_commit_push"), jobs_before + 1)

    def test_github_invalid_signature_is_rejected(self):
        jobs_before = self._job_count("_process_commit_push")
        result = self._post_webhook(
            self._load_payload("github_push.json"),
            headers={"X-Hub-Signature-256": f"sha256={'0' * 64}"},
        )
        self.assertIs(result, False)
        self.assertEqual(self._job_count("_process_commit_push"), jobs_before)

    def test_missing_token_param_rejects_requests(self):
        # Without a configured authorization token every request is
        # rejected, even when its headers would otherwise match
        self.config.set_param("webhook_gitlab.authorization_token", False)
        jobs_before = self._job_count("_process_commit_push")
        result = self._post_webhook(
            self._load_payload("gitlab_push.json"),
            headers={"X-Gitlab-Event": "Push Hook", "X-Gitlab-Token": TEST_TOKEN},
        )
        self.assertIs(result, False)
        self.assertEqual(self._job_count("_process_commit_push"), jobs_before)

    def test_insecure_default_token_rejects_requests(self):
        # The demo default "token" is publicly known: a webhook sending
        # the matching header must be rejected anyway
        self.config.set_param("webhook_gitlab.authorization_token", "token")
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

    def test_github_event_without_known_kind_is_skipped(self):
        # GitHub events are classified by their keys (pull_request /
        # pusher): anything else (e.g. the ping event) gets no
        # project_git_event_type and is acknowledged without enqueueing
        # anything
        payload = {"zen": "Design for failure.", "hook_id": 1, "repository": {}}
        jobs_total_before = self.env["queue.job"].sudo().search_count([])
        result = self._post_webhook(
            payload,
            headers={"X-Hub-Signature-256": self._github_signature(payload)},
        )
        self.assertIs(result, True)
        self.assertEqual(
            self.env["queue.job"].sudo().search_count([]), jobs_total_before
        )
