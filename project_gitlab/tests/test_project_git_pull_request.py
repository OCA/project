# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from psycopg2 import IntegrityError

from odoo.tools import mute_logger

from .common import GITLAB_REPO_URL, ProjectGitlabCase


class TestGitlabPullRequestModel(ProjectGitlabCase):
    def test_mr_identifiers_unique_within_platform(self):
        # SQL constraint guarding the search-then-create dedup of the
        # event flow against concurrent jobs on the same MR
        pull_request_vals = {
            "name": "GitLab MR",
            "source": "gitlab",
            "id_project": 1001,
            "id_request": 1,
        }
        self.env["project.git.pull.request"].create(pull_request_vals)
        with (
            self.assertRaises(IntegrityError),
            mute_logger("odoo.sql_db"),
            self.env.cr.savepoint(),
        ):
            self.env["project.git.pull.request"].create(
                dict(pull_request_vals, name="GitLab MR duplicate")
            )

    def test_post_message_without_event_connects_via_record_url(self):
        # Without an event the GitLab connection URL falls back to the
        # record MR URL (modern /-/merge_requests/ layout); the event,
        # when present, stays the preferred source.
        pull_request = self.env["project.git.pull.request"].create(
            {
                "name": "GL-100 fallback",
                "source": "gitlab",
                "url": f"{GITLAB_REPO_URL}/-/merge_requests/7",
                "id_request": 7,
                "id_project": 1001,
                "state": "opened",
            }
        )
        patcher, merge_request = self._mock_gitlab_client()
        with patcher as connect_gitlab:
            pull_request._post_message("fallback message")

        self.assertEqual(connect_gitlab.call_args.kwargs.get("url"), GITLAB_REPO_URL)
        merge_request.discussions.create.assert_called_once_with(
            {"body": "fallback message"}
        )
