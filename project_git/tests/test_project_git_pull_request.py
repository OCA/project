# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import ProjectGitCase


class TestProjectGitPullRequest(ProjectGitCase):
    def test_pull_requests_without_source_do_not_collide(self):
        # The uniqueness of (source, id_project, id_request) only binds
        # records of the same platform: records without a source (e.g.
        # created by hand) never collide with each other (NULLs are
        # distinct for the constraint). The collision case needs a real
        # source value, so it is covered by the bridge suites.
        for name in ("First sourceless PR", "Second sourceless PR"):
            self.env["project.git.pull.request"].create(
                {"name": name, "id_project": 1, "id_request": 1}
            )
        self.env.flush_all()
