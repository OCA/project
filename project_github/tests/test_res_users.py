# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError

from .common import ProjectGithubCase


class TestGithubResUsers(ProjectGithubCase):
    def test_github_username_must_be_unique(self):
        # The PR author matching picks one user per username: a
        # duplicate github_username is rejected (Python constraint)
        self.env["res.users"].create(
            {
                "name": "GitHub User One",
                "login": "github-user-one@example.com",
                "github_username": "gh-duplicate-user",
            }
        )
        with self.assertRaises(ValidationError):
            self.env["res.users"].create(
                {
                    "name": "GitHub User Two",
                    "login": "github-user-two@example.com",
                    "github_username": "gh-duplicate-user",
                }
            )
