# Copyright 2020, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    github_username = fields.Char()

    @api.constrains("github_username")
    def _check_github_username_unique(self):
        # A GitHub username must identify a single Odoo user: the PR
        # author matching picks one user per username
        for user in self.filtered("github_username"):
            duplicate_user = (
                self.sudo()
                .with_context(active_test=False)
                .search(
                    [
                        ("github_username", "=", user.github_username),
                        ("id", "!=", user.id),
                    ],
                    limit=1,
                )
            )
            if duplicate_user:
                raise ValidationError(
                    _(
                        'GitHub username "%(username)s" is already assigned'
                        " to user %(user)s.",
                        username=user.github_username,
                        user=duplicate_user.name,
                    )
                )
