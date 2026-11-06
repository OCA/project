# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from github import Github

from odoo import api, models


class ProjectGitAuth(models.AbstractModel):
    _inherit = "project.git.auth"

    @api.model
    def _connect_github(self):
        """Connect to github instance and return github object"""
        return Github(self._get_token_param("project_github.token"))
