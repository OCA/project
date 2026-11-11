# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os
from copy import deepcopy
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from odoo.addons.project_git.tests.common import (
    GITHUB_REPO_URL,
    NULL_SHA,
    ProjectGitCase,
)
from odoo.addons.project_github.controllers.main import ProjectGithubWebhook
from odoo.addons.project_github.models.project_git_auth import ProjectGitAuth

__all__ = ["GITHUB_REPO_URL", "NULL_SHA", "ProjectGithubCase"]


class ProjectGithubCase(ProjectGitCase):
    """GitHub flavor of the state-based webhook case: dispatches the
    payloads through the GitHub controller parser and mocks the
    PyGithub client."""

    RES_DIR = os.path.join(os.path.dirname(__file__), "res")

    def _dispatch(self, payload, source, headers=None):
        """Normalize the payload like the controller does, then run the
        matching ``_process_*`` handler synchronously.

        The event type travels in the X-GitHub-Event header: when not
        given explicitly, the header a real delivery would carry is
        derived from the payload shape."""
        event = deepcopy(payload)
        event["source"] = source
        if headers is None:
            event_name = "pull_request" if payload.get("pull_request") else "push"
            headers = {"X-GitHub-Event": event_name}
        event = ProjectGithubWebhook()._parse_git_request_data(
            event=event, headers=headers
        )
        # Event types the source binds no handler for (e.g. tag_push)
        # are skipped, like the controller does
        method_name = f"_process_{event['project_git_event_type']}_{source}"
        if hasattr(self.git_event, method_name):
            getattr(self.git_event, method_name)(event)
        return event

    # ---- outbound API mocks ----

    # Commit stubs are SimpleNamespace on purpose (not MagicMock): the
    # handlers read commit fields via getattr(..., None), so a permissive
    # mock would never expose missing fields and the lazy-loading paths
    # would go untested.

    @staticmethod
    def _github_commit_stub(sha, message, url=None):
        """Commit object as returned by PyGithub."""
        author = SimpleNamespace(
            name="Demo User",
            email="demo@example.com",
            date=datetime(2026, 1, 1, 10, 0, 0),
        )
        return SimpleNamespace(
            sha=sha,
            commit=SimpleNamespace(message=message, author=author),
            html_url=url or f"{GITHUB_REPO_URL}/commit/{sha}",
        )

    def _mock_github_client(self, commits=()):
        """Return (patcher, pull request mock) replacing _connect_github.

        The pull request mock serves both the PR commit fetch
        (pull.get_commits()) and the message posting
        (pull.create_issue_comment).
        """
        client = MagicMock(name="github_client")
        pull = client.get_repo.return_value.get_pull.return_value
        pull.get_commits.return_value = [
            self._github_commit_stub(**commit) for commit in commits
        ]
        patcher = patch.object(ProjectGitAuth, "_connect_github", return_value=client)
        return patcher, pull
