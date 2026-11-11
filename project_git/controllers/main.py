# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import functools
import logging

from odoo import http
from odoo.http import request

from ..models.project_git_auth import BANNED_TOKENS

_logger = logging.getLogger(__name__)


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
            .get_param("project_git.authorization_token")
        )
        if not token or token in BANNED_TOKENS:
            _logger.warning(
                "project_git.authorization_token is not configured "
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
        if hasattr(self, f"_verify_webhook_token_{source}"):
            authorization = getattr(self, f"_verify_webhook_token_{source}")(token)
        if not authorization:
            _logger.warning("Token is not the expected for source %r", source)
            return False
        kw["source"] = source
        return function(self, *args, **kw)

    return wrapper


class ProjectGitWebhook(http.Controller):
    @http.route("/project_git/webhook/", type="json", auth="public", csrf=False)
    @token_authorization
    def _process_webhook(self, **kw):
        """Receive the request from the git platform and invoke the
        per-source handler named after the normalized
        'project_git_event_type' key and the event source:
        _process_<project_git_event_type>_<source>. Each platform
        bridge explicitly binds every event it handles."""
        event = request.get_json_data()
        event["source"] = kw.get("source", "")
        event = self._parse_git_request_data(
            event=event, headers=request.httprequest.headers
        )
        git_event = request.env["project.git.event"]
        event_type = event.get("project_git_event_type")
        if not event_type:
            return True
        method_name = f"_process_{event_type}_{event['source']}"
        if not hasattr(git_event, method_name):
            # Event kinds the source bridge binds no handler for
            # (e.g. note events) are skipped silently.
            return True
        return getattr(git_event.with_delay(), method_name)(event)

    def _detect_event_source(self, headers):
        """Recognize the source platform of a request from its headers.

        Each platform bridge claims its own specific header (claim first,
        then super()); requests that no platform claims map to an empty
        source (and are then rejected by the token authorization).
        """
        return ""

    def _parse_git_request_data(self, event, headers=None):
        """The structure of a git request differ among different sources
        (e.g. github vs gitlab). This method dispatches to the
        source-specific parser, which fetches necessary data, creates a
        new 'common key' in the request object and puts the data inside
        it so it's easy to retrieve it later despite the source.

        The event type lands in the module-owned
        'project_git_event_type' key: each parser maps the
        authoritative discriminator of its platform onto it (some
        platforms carry it in the payload, others in a request header
        — hence the headers argument). Push events are then refined into their
        concrete type (branch_creation, branch_deletion, commit_push),
        so that project_git_event_type, together with the source,
        always names the project.git.event handler to invoke."""

        if not hasattr(self, f"_parse_git_request_data_{event.get('source')}"):
            _logger.warning(
                "No request parser implementation for source %r", event.get("source")
            )
            return event
        event = getattr(self, f"_parse_git_request_data_{event.get('source')}")(
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
