# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from urllib.parse import urljoin

import gitlab  # pylint: disable=W7935
from github import Github

from odoo import api, models


class GitAuth(models.AbstractModel):
    _name = "git.auth"
    _description = "Git Platform Authentication"

    @api.model
    def _connect_gitlab(self, url):
        """Connect to the gitlab instance hosting the given project URL
        and return the gitlab client object.

        :param str url: a project-level URL (e.g. project web_url); the
            instance root is derived from it, and selects the per-instance
            token sysparam (webhook_gitlab.gitlab_token.<instance root>)
        """
        url = urljoin(url, "../..")
        token = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("webhook_gitlab.gitlab_token." + url)
        )
        return gitlab.Gitlab(url, private_token=token)

    @api.model
    def _connect_github(self):
        """Connect to github instance and return github object"""
        token = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("webhook_gitlab.github_token")
        )
        return Github(token)
