# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from odoo.addons.project_git.tests.common import (
    GITLAB_REPO_URL,
    NULL_SHA,
    ProjectGitCase,
)
from odoo.addons.project_gitlab.controllers.main import ProjectGitlabWebhook
from odoo.addons.project_gitlab.models.project_git_auth import ProjectGitAuth

__all__ = ["GITLAB_REPO_URL", "NULL_SHA", "ProjectGitlabCase"]


class ProjectGitlabCase(ProjectGitCase):
    """GitLab flavor of the state-based webhook case: dispatches the
    payloads through the GitLab controller parser and mocks the
    python-gitlab client."""

    RES_DIR = os.path.join(os.path.dirname(__file__), "res")

    def _dispatch(self, payload, source, headers=None):
        """Normalize the payload like the controller does, then run the
        matching ``_process_*`` handler synchronously."""
        event = deepcopy(payload)
        event["source"] = source
        event = ProjectGitlabWebhook()._parse_git_request_data(
            event=event, headers=headers
        )
        # Event types without a handler (e.g. tag_push) are skipped,
        # like the controller does
        if hasattr(self.git_event, "_process_%s" % event["project_git_event_type"]):
            getattr(self.git_event, "_process_%s" % event["project_git_event_type"])(
                event
            )
        return event

    # ---- outbound API mocks ----

    # Commit stubs are SimpleNamespace on purpose (not MagicMock): the
    # handlers read commit fields via getattr(..., None), so a permissive
    # mock would never expose missing fields and the lazy-loading paths
    # would go untested.

    @staticmethod
    def _gitlab_commit_stub(sha, message, url=None):
        """Commit object as returned by python-gitlab (all fields loaded)."""
        return SimpleNamespace(
            id=sha,
            message=message,
            title=message.split("\n", 1)[0],
            web_url=url or f"{GITLAB_REPO_URL}/-/commit/{sha}",
            created_at="2026-01-01T10:00:00+00:00",
            author_name="Demo User",
            author_email="demo@example.com",
        )

    def _mock_gitlab_client(self, commits=()):
        """Return (patcher, merge request mock) replacing _connect_gitlab.

        The merge request mock serves both the MR commit fetch
        (mr.commits()) and the message posting (mr.discussions.create).
        """
        client = MagicMock(name="gitlab_client")
        merge_request = client.projects.get.return_value.mergerequests.get.return_value
        merge_request.commits.return_value = [
            self._gitlab_commit_stub(**commit) for commit in commits
        ]
        patcher = patch.object(ProjectGitAuth, "_connect_gitlab", return_value=client)
        return patcher, merge_request
