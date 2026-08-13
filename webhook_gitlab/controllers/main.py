# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import functools
import logging
from hashlib import sha256
from hmac import HMAC, compare_digest

from odoo import http
from odoo.http import request
from odoo.tools import consteq

_logger = logging.getLogger(__name__)

# Values of webhook_gitlab.authorization_token that must never authorize a
# webhook: the default shipped by the module demo data is publicly known.
INSECURE_AUTHORIZATION_TOKENS = ("token",)


def token_authorization(function):
    """Decorator for controllers with token authorization.

    The event source is recognized from the request headers
    (_detect_event_source), then the request is authorized by the
    source-specific _verify_webhook_token_<source> method. Requests from
    unrecognized sources or with an invalid token get an unsuccessful
    response.
    """

    @functools.wraps(function)
    def wrapper(self, *args, **kw):
        token = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("webhook_gitlab.authorization_token")
        )
        if not token or token in INSECURE_AUTHORIZATION_TOKENS:
            _logger.warning(
                "webhook_gitlab.authorization_token is not configured "
                "(or still set to an insecure default)"
            )
            return False
        source = self._detect_event_source(request.httprequest.headers)
        if not source:
            _logger.warning(
                "Unrecognized webhook source (no platform header claims the request)"
            )
            return False
        authorization = False
        if hasattr(self, "_verify_webhook_token_%s" % source):
            authorization = getattr(self, "_verify_webhook_token_%s" % source)(token)
        if not authorization:
            _logger.warning("Token is not the expected for source %r", source)
            return False
        kw["source"] = source
        return function(self, *args, **kw)

    return wrapper


class WebhookGitlab(http.Controller):
    @http.route("/webhook_gitlab/webhook/", type="json", auth="public", csrf=False)
    @token_authorization
    def _process_webhook(self, **kw):
        """Receive the request from Gitlab/Github and invoke functions based on
        the normalized 'project_git_event_type' key, then it calls the
        function with the name _process_<project_git_event_type>."""
        event = request.get_json_data()
        event["source"] = kw.get("source", "")
        event = self._parse_git_request_data(
            event=event, headers=request.httprequest.headers
        )
        git_event = request.env["git.event"]
        event_type = event.get("project_git_event_type")
        if not event_type:
            return True
        method_name = "_process_%s" % event_type
        if not hasattr(git_event, method_name):
            # Event kinds without a handler (e.g. note
            # events) are skipped silently.
            return True
        return getattr(git_event.with_delay(), method_name)(event)

    def _detect_event_source(self, headers):
        """Recognize the source platform of a request from its headers.

        Each platform claims its own specific header; requests that no
        platform claims map to an empty source (and are then rejected by
        the token authorization).
        """
        if headers.get("X-Gitlab-Event"):
            return "gitlab"
        if headers.get("X-Hub-Signature-256"):
            return "github"
        return ""

    def _verify_webhook_token_gitlab(self, token):
        """GitLab sends the webhook token verbatim in a request header."""
        gitlab_token = request.httprequest.headers.get("X-Gitlab-Token", "")
        return consteq(gitlab_token, token)

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

    def _parse_git_request_data(self, event, headers=None):
        """The structure of a git request differ among different sources
        (e.g. github vs gitlab). This method dispatches to the
        source-specific parser, which fetches necessary data, creates a
        new 'common key' in the request object and puts the data inside
        it so it's easy to retrieve it later despite the source.

        The event type lands in the module-owned
        'project_git_event_type' key: each parser maps the
        authoritative discriminator of its platform onto it (GitLab
        carries it in the payload, GitHub in a request header — hence
        the headers argument). Push events are then refined into their
        concrete type (branch_creation, branch_deletion, commit_push),
        so that project_git_event_type always names the git.event
        handler to invoke."""

        if not hasattr(self, "_parse_request_%s" % event.get("source")):
            _logger.warning(
                "No request parser implementation for source %r", event.get("source")
            )
            return event
        event = getattr(self, "_parse_request_%s" % event.get("source"))(
            event=event, headers=headers
        )
        if event.get("project_git_event_type") == "push":
            event["project_git_event_type"] = self._classify_push_event(event)
        return event

    def _classify_push_event(self, event):
        """
        Classify push event type based on before/after SHA values.
        Returns: 'branch_creation', 'branch_deletion', 'commit_push', or
        an empty string for degenerate pushes (both SHAs null), which
        are then dropped by the explicit no-type guard of the dispatch.

        The null-SHA convention on before/after is git's own push
        schema, not a platform convention: platforms usually carry it
        verbatim in their push payloads, so the classification is
        shared by every source.
        """
        NULL_SHA = "0000000000000000000000000000000000000000"
        before = event.get("before", "")
        after = event.get("after", "")

        if before == NULL_SHA and after != NULL_SHA:
            return "branch_creation"
        elif before != NULL_SHA and after == NULL_SHA:
            return "branch_deletion"
        elif before != NULL_SHA and after != NULL_SHA:
            return "commit_push"
        return ""

    def _parse_request_gitlab(self, event, headers=None):
        # GitLab carries its authoritative event discriminator in the
        # payload: map it onto the module-owned key (headers unused)
        event["project_git_event_type"] = event.get("object_kind")
        event["repository_url"] = event.get("project", {}).get("git_http_url")
        return event

    def _parse_request_github(self, event, headers=None):
        # Github carries its authoritative event discriminator in the
        # X-GitHub-Event request header, not in the payload; event
        # types without a git.event handler (e.g. ping) are then
        # skipped by the dispatch
        event["project_git_event_type"] = (headers or {}).get("X-GitHub-Event", "")
        # GitHub delivers tag pushes as regular push events: remap them
        # onto the handlerless tag_push type (the one GitLab tag pushes
        # carry natively), so they are skipped instead of being tracked
        # as branches
        if event["project_git_event_type"] == "push" and not event.get(
            "ref", ""
        ).startswith("refs/heads/"):
            event["project_git_event_type"] = "tag_push"
        # set repo url
        event["repository_url"] = event.get("repository", {}).get("html_url")
        return event
