# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tools import mute_logger

from .common import ProjectGitCase


class TestProjectGitPullRequest(ProjectGitCase):
    def test_pull_request_without_source_assigns_no_tags(self):
        # The tags master-data lives in the bridges: without a source
        # there is no module to resolve the tag records from, so the
        # tag assignment is skipped instead of crashing
        with mute_logger("odoo.addons.project_git.models.project_git_pull_request"):
            self.env["project.git.pull.request"].create(
                {
                    "name": "Sourceless PR with state",
                    "id_project": 7,
                    "id_request": 7,
                    "state": "opened",
                    "task_ids": [(4, self.gl_task_100.id)],
                }
            )
        self.assertFalse(
            [
                tag_name
                for tag_name in self.gl_task_100.tag_ids.mapped("name")
                if tag_name.startswith("MR:")
            ]
        )

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
