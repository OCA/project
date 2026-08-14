# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from psycopg2 import IntegrityError

from odoo.tools import mute_logger

from .common import ProjectGitCase


class TestSqlConstraints(ProjectGitCase):
    # The event flow deduplicates with search-then-create: the SQL
    # constraints guard the identifying keys against concurrent jobs
    # processing the same entity

    def test_commit_full_sha_unique(self):
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

    def test_branch_url_unique(self):
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

    def test_pull_requests_without_source_do_not_collide(self):
        # The uniqueness of (source, id_project, id_request) only binds
        # records of the same platform: records without a source (e.g.
        # created by hand) never collide with each other (NULLs are
        # distinct for the constraint)
        for name in ("First sourceless PR", "Second sourceless PR"):
            self.env["project.git.pull.request"].create(
                {"name": name, "id_project": 1, "id_request": 1}
            )
        self.env.flush_all()
