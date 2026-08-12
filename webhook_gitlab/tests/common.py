# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json
import os
from copy import deepcopy
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase

from odoo.addons.webhook_gitlab.controllers.main import WebhookGitlab
from odoo.addons.webhook_gitlab.models.git_event import (
    DEFAULT_TASK_NAME_MATCH_REGEX,
    GitEvent,
)

RES_DIR = os.path.join(os.path.dirname(__file__), "res")

GITLAB_REPO_URL = "https://gitlab.example.com/acme/demo-repo"
GITHUB_REPO_URL = "https://github.example.com/acme/webhook-demo"
NULL_SHA = "0" * 40


class WebhookGitlabCase(TransactionCase):
    """Base case for state-based webhook tests.

    Payloads (tests/res/*.json) are real captured webhook requests stripped
    down to the keys the module consumes. They are normalized through the
    actual controller parsing helpers and dispatched synchronously to the
    git.event handlers, so the whole processing chain runs except
    HTTP transport, authentication and the job queue.
    Outbound API traffic (python-gitlab / PyGithub) is mocked.

    Tests assert the resulting state (entities created and their links),
    not the internal call flow, so they should survive refactorings that
    keep behavior unchanged.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.git_event = cls.env["git.event"]
        cls.env["ir.config_parameter"].sudo().set_param(
            "webhook_gitlab.task_name_match_regex", DEFAULT_TASK_NAME_MATCH_REGEX
        )
        Project = cls.env["project.project"]
        Task = cls.env["project.task"]
        # Neutralize pre-existing projects pointing to git repos (leftovers
        # from manual testing in the devel database) so they cannot interfere
        # with repository matching. Rolled back at the end of the test class.
        Project.search(
            [
                "|",
                ("git_project_url", "!=", False),
                ("git_dev_project_url", "!=", False),
            ]
        ).write({"git_project_url": False, "git_dev_project_url": False})
        # Snapshot pre-existing git entities (devel database leftovers) so
        # the state helpers only ever see records created by the tests.
        cls._initial_branch_ids = cls.env["git.branch"].sudo().search([]).ids
        cls._initial_commit_ids = cls.env["git.commit"].sudo().search([]).ids
        cls._initial_pr_ids = cls.env["git.pull.request"].sudo().search([]).ids
        cls.gitlab_project = Project.create(
            {"name": "GitLab Repo", "git_project_url": f"{GITLAB_REPO_URL}.git"}
        )
        cls.github_project = Project.create(
            {"name": "GitHub Repo", "git_project_url": GITHUB_REPO_URL}
        )
        # Same fixture layout on both platforms: two tasks with a matchable
        # pattern (spaced numbering, scalable by steps of 15) plus one task
        # without pattern to assert it is never touched.
        cls.gl_task_100 = Task.create(
            {"name": "GL-100 implement feature", "project_id": cls.gitlab_project.id}
        )
        cls.gl_task_115 = Task.create(
            {"name": "GL-115 fix bug", "project_id": cls.gitlab_project.id}
        )
        cls.gl_task_no_pattern = Task.create(
            {"name": "GitLab task without pattern", "project_id": cls.gitlab_project.id}
        )
        cls.gh_task_100 = Task.create(
            {"name": "GH-100 improve readme", "project_id": cls.github_project.id}
        )
        cls.gh_task_115 = Task.create(
            {"name": "GH-115 add docs", "project_id": cls.github_project.id}
        )
        cls.gh_task_no_pattern = Task.create(
            {"name": "GitHub task without pattern", "project_id": cls.github_project.id}
        )

    # ---- payload helpers ----

    @staticmethod
    def _load_payload(name):
        with open(os.path.join(RES_DIR, name), encoding="utf-8") as payload_file:
            return json.load(payload_file)

    def _dispatch(self, payload, source):
        """Normalize the payload like the controller does, then run the
        matching ``_process_*`` handler synchronously."""
        event = deepcopy(payload)
        event["source"] = source
        event = WebhookGitlab()._parse_git_request_data(event=event)
        handler = getattr(self.git_event, "_process_%s" % event["object_kind"])
        handler(event)
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
        patcher = patch.object(GitEvent, "_connect_gitlab", return_value=client)
        return patcher, merge_request

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
        patcher = patch.object(GitEvent, "_connect_github", return_value=client)
        return patcher, pull

    # ---- state helpers ----

    def _get_branch(self, name):
        return self.env["git.branch"].search(
            [("name", "=", name), ("id", "not in", self._initial_branch_ids)]
        )

    def _get_commit(self, sha):
        return self.env["git.commit"].search(
            [("full_sha", "=", sha), ("id", "not in", self._initial_commit_ids)]
        )

    def _get_pull_request(self, url):
        return self.env["git.pull.request"].search(
            [("url", "=", url), ("id", "not in", self._initial_pr_ids)]
        )
