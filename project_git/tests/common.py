# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json
import os

from odoo.tests.common import HttpCase, TransactionCase

GITLAB_REPO_URL = "https://gitlab.example.com/acme/demo-repo"
GITHUB_REPO_URL = "https://github.example.com/acme/webhook-demo"
NULL_SHA = "0" * 40

TEST_TOKEN = "unit-test-webhook-secret"
WEBHOOK_URL = "/project_git/webhook/"


class PayloadCaseMixin:
    """Loader for the webhook payload fixtures of the bridge test
    modules: each bridge points RES_DIR to its own tests/res directory."""

    RES_DIR = None

    @classmethod
    def _load_payload(cls, name):
        with open(os.path.join(cls.RES_DIR, name), encoding="utf-8") as payload_file:
            return json.load(payload_file)


class ProjectGitCase(PayloadCaseMixin, TransactionCase):
    """Base case for state-based webhook tests.

    Payloads (tests/res/*.json of the bridge modules) are real captured
    webhook requests stripped down to the keys the modules consume. They
    are normalized through the actual controller parsing helpers and
    dispatched synchronously to the project.git.event handlers, so the
    whole processing chain runs except HTTP transport, authentication
    and the job queue (those layers are covered with real requests in
    the test_controller.py files). Outbound API traffic (python-gitlab /
    PyGithub) is mocked by the bridge test cases.

    Tests assert the resulting state (entities created and their links),
    not the internal call flow, so they should survive refactorings that
    keep behavior unchanged. Within that style, the suite aims to cover
    every code area of the modules: controller authorization, event
    handlers and state transitions, matching and configuration edge cases.

    The project/task fixtures cover both platforms regardless of the
    installed bridges: they are plain neutral data, shared so that the
    bridge suites stay symmetric.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.git_event = cls.env["project.git.event"]
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
        cls._initial_branch_ids = cls.env["project.git.branch"].sudo().search([]).ids
        cls._initial_commit_ids = cls.env["project.git.commit"].sudo().search([]).ids
        cls._initial_pr_ids = cls.env["project.git.pull.request"].sudo().search([]).ids
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

    # ---- state helpers ----

    def _get_branch(self, name):
        return self.env["project.git.branch"].search(
            [("name", "=", name), ("id", "not in", self._initial_branch_ids)]
        )

    def _get_commit(self, sha):
        return self.env["project.git.commit"].search(
            [("full_sha", "=", sha), ("id", "not in", self._initial_commit_ids)]
        )

    def _get_pull_request(self, url):
        return self.env["project.git.pull.request"].search(
            [("url", "=", url), ("id", "not in", self._initial_pr_ids)]
        )


class ProjectGitControllerCase(PayloadCaseMixin, HttpCase):
    """Base case for real HTTP requests against the webhook route,
    covering the layers that the state-based suite bypasses on purpose:
    the token authorization decorator and the event dispatch. Accepted
    events are only checked up to the queue job enqueueing (the
    processing itself is covered by the state-based suite)."""

    def setUp(self):
        super().setUp()
        self.config = self.env["ir.config_parameter"].sudo()
        self.config.set_param("project_git.authorization_token", TEST_TOKEN)

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

    def _job_count(self, method_name):
        return (
            self.env["queue.job"]
            .sudo()
            .search_count([("method_name", "=", method_name)])
        )
