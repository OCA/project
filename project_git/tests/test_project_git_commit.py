# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from psycopg2 import IntegrityError

from odoo.tools import mute_logger

from .common import ProjectGitCase


class TestProjectGitCommit(ProjectGitCase):
    def test_commit_full_sha_unique(self):
        # The event flow deduplicates with search-then-create: the SQL
        # constraint guards the identifying key against concurrent jobs
        # processing the same commit
        self.env["project.git.commit"].create(
            {"name": "GL-100 first", "full_sha": "a" * 40}
        )
        with (
            self.assertRaises(IntegrityError),
            mute_logger("odoo.sql_db"),
            self.env.cr.savepoint(),
        ):
            self.env["project.git.commit"].create(
                {"name": "GL-100 duplicate", "full_sha": "a" * 40}
            )
