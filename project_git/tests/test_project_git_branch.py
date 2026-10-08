# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from psycopg2 import IntegrityError

from odoo.tools import mute_logger

from .common import ProjectGitCase


class TestProjectGitBranch(ProjectGitCase):
    def test_branch_url_unique(self):
        # The event flow deduplicates with search-then-create: the SQL
        # constraint guards the identifying key against concurrent jobs
        # processing the same branch
        branch_url = "https://gitlab.example.com/acme/demo-repo/-/tree/GL-100-feature"
        self.env["project.git.branch"].create(
            {"name": "GL-100-feature", "url": branch_url}
        )
        with (
            self.assertRaises(IntegrityError),
            mute_logger("odoo.sql_db"),
            self.env.cr.savepoint(),
        ):
            self.env["project.git.branch"].create(
                {"name": "GL-100-feature", "url": branch_url}
            )
