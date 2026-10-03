# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from psycopg2 import IntegrityError

from odoo.tools import mute_logger

from .common import ProjectGithubCase


class TestGithubPullRequestModel(ProjectGithubCase):
    def test_pr_identifiers_unique_within_platform(self):
        # SQL constraint guarding the search-then-create dedup of the
        # event flow against concurrent jobs on the same PR
        pull_request_vals = {
            "name": "GitHub PR",
            "source": "github",
            "id_project": 2002,
            "id_request": 2,
        }
        self.env["project.git.pull.request"].create(pull_request_vals)
        with (
            self.assertRaises(IntegrityError),
            mute_logger("odoo.sql_db"),
            self.env.cr.savepoint(),
        ):
            self.env["project.git.pull.request"].create(
                dict(pull_request_vals, name="GitHub PR duplicate")
            )
