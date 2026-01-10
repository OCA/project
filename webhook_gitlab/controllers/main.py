# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import functools
import logging
from hashlib import sha256
from hmac import HMAC, compare_digest

from odoo import http
from odoo.http import request
from odoo.tools import consteq

_logger = logging.getLogger(__name__)


def token_authorization(function):
    """Decorator for controllers with token authorization.
    it allows only requests with X-Gitlab-Token or X-Hub-Signature-256 header present.

    Will returns an unsuccessful response whenever the token
    is invalid.
    """

    @functools.wraps(function)
    def wrapper(self, *args, **kw):
        headers = request.httprequest.headers
        gitlab_token = headers.get("X-Gitlab-Token")
        github_token = headers.get("X-Hub-Signature-256")
        token = request.env["ir.config_parameter"].sudo().get_param("webhook_gitlab.authorization_token")
        kw["source"] = ""
        if github_token:
            expected_token = HMAC(
                key=token.encode("utf-8"),
                msg=request.httprequest.data,
                digestmod=sha256,
            ).hexdigest()
            authorization = compare_digest(github_token.split("sha256=")[-1].strip(), expected_token)
            kw["source"] = "github"
        elif gitlab_token:
            authorization = consteq(gitlab_token, token)
            kw["source"] = "gitlab"
        if not authorization:
            _logger.warning("Token is not the expected")
            return False
        return function(self, *args, **kw)

    return wrapper


class WebhookGitlab(http.Controller):

    @http.route("/webhook_gitlab/webhook/", type="json", auth="public", csrf=False)
    @token_authorization
    def _process_webhook(self, **kw):
        """Receive the request from Gitlab/Github and invoke functions based on
        'object_kind', then it calls the function with the name
        _process_<object_kind>."""
        event = request.get_json_data()
        event["source"] = kw.get("source", "")
        event = self._parse_git_request_data(event=event)
        git_event = request.env["git.event"]
        object_kind = event.get("object_kind")
        if not object_kind:
            return True
        method_name = "_process_%s" % object_kind
        if not hasattr(git_event, method_name):
            # Event kinds without a handler (e.g. note
            # events) are skipped silently.
            return True
        return getattr(git_event.with_delay(), method_name)(event)

    def _parse_git_request_data(self, event):
        """The structure of a git request differ among different sources
        (e.g. github vs gitlab). This method will fetch necessary data
        accordingly to the current source, create a new 'common key' in
        the request object and put the data inside it so it's easy to
        retrieve it later despite the source."""

        source = event.get("source")
        if source == "github":
            event = self._parse_request_github(event=event)
        elif not source or source == "gitlab":
            event = self._parse_request_gitlab(event=event)

        return event

    def _parse_request_gitlab(self, event):
        event["repository_url"] = event.get("project", {}).get("git_http_url")
        return event

    def _parse_request_github(self, event):
        # Github doesn't have an explicit `object_kind` key.
        # We guess the object kind by looking for specific events
        # in the request.
        if event.get("pull_request", {}):
                event["object_kind"] = "pull_request"
        elif event.get("pusher"):
            event["object_kind"] = "push"
        # set repo url
        event["repository_url"] = event.get("repository", {}).get("html_url")
        return event
