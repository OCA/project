# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests import tagged

from .common import ProjectGitControllerCase


@tagged("post_install", "-at_install")
class TestWebhookController(ProjectGitControllerCase):
    """Platform-agnostic authorization layers: requests that no platform
    claims and requests arriving without a configured token. The
    platform-specific verifications (GitLab token, GitHub signature) are
    covered by the bridge test suites."""

    def test_request_without_auth_headers_is_rejected(self):
        # No platform header claims the request: the source stays
        # unrecognized and the request is rejected even with a valid
        # token configured
        jobs_before = self._job_count("_process_commit_push")
        result = self._post_webhook({"object_kind": "push"})
        self.assertIs(result, False)
        self.assertEqual(self._job_count("_process_commit_push"), jobs_before)

    def test_missing_token_param_rejects_requests(self):
        # Without a configured authorization token every request is
        # rejected before any source detection
        self.config.set_param("project_git.authorization_token", False)
        jobs_before = self._job_count("_process_commit_push")
        result = self._post_webhook({"object_kind": "push"})
        self.assertIs(result, False)
        self.assertEqual(self._job_count("_process_commit_push"), jobs_before)
