# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from hashlib import sha256
from hmac import HMAC, compare_digest

from odoo.http import request

from odoo.addons.project_git.controllers.main import ProjectGitWebhook


class ProjectGithubWebhook(ProjectGitWebhook):
    def _detect_event_source(self, headers):
        # GitHub claims its requests by its specific signature header
        if headers.get("X-Hub-Signature-256"):
            return "github"
        return super()._detect_event_source(headers)

    def _verify_webhook_token_github(self, token):
        """GitHub signs the request body with the webhook secret
        (HMAC-SHA256) instead of sending the secret itself."""
        signature = request.httprequest.headers.get("X-Hub-Signature-256", "")
        expected_token = HMAC(
            key=token.encode("utf-8"),
            msg=request.httprequest.data,
            digestmod=sha256,
        ).hexdigest()
        return compare_digest(signature.split("sha256=")[-1].strip(), expected_token)

    def _parse_git_request_data_github(self, event, headers=None):
        # Github carries its authoritative event discriminator in the
        # X-GitHub-Event request header, not in the payload; event
        # types without a project.git.event handler (e.g. ping) are
        # then skipped by the dispatch
        event["project_git_event_type"] = (headers or {}).get("X-GitHub-Event", "")
        # GitHub delivers tag pushes as regular push events: remap them
        # onto the handlerless normalized tag_push type, so they are
        # skipped instead of being tracked as branches
        if event["project_git_event_type"] == "push" and not event.get(
            "ref", ""
        ).startswith("refs/heads/"):
            event["project_git_event_type"] = "tag_push"
        # set repo url
        event["repository_url"] = event.get("repository", {}).get("html_url")
        return event
