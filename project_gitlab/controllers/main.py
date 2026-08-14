# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.http import request
from odoo.tools import consteq

from odoo.addons.project_git.controllers.main import ProjectGitWebhook


class ProjectGitlabWebhook(ProjectGitWebhook):
    def _detect_event_source(self, headers):
        # GitLab claims its requests by its specific event header
        if headers.get("X-Gitlab-Event"):
            return "gitlab"
        return super()._detect_event_source(headers)

    def _verify_webhook_token_gitlab(self, token):
        """GitLab sends the webhook token verbatim in a request header."""
        gitlab_token = request.httprequest.headers.get("X-Gitlab-Token", "")
        return consteq(gitlab_token, token)

    def _parse_request_gitlab(self, event, headers=None):
        # GitLab carries its authoritative event discriminator in the
        # payload: map it onto the module-owned key (headers unused)
        event["project_git_event_type"] = event.get("object_kind")
        event["repository_url"] = event.get("project", {}).get("git_http_url")
        return event
