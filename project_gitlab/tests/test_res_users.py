# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError

from .common import ProjectGitlabCase


class TestGitlabResUsers(ProjectGitlabCase):
    def test_gitlab_username_must_be_unique(self):
        # The PR author matching picks one user per username: a
        # duplicate gitlab_username is rejected (Python constraint)
        self.env["res.users"].create(
            {
                "name": "GitLab User One",
                "login": "gitlab-user-one@example.com",
                "gitlab_username": "gl-duplicate-user",
            }
        )
        with self.assertRaises(ValidationError):
            self.env["res.users"].create(
                {
                    "name": "GitLab User Two",
                    "login": "gitlab-user-two@example.com",
                    "gitlab_username": "gl-duplicate-user",
                }
            )
