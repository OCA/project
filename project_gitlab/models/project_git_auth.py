# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from urllib.parse import urljoin

import gitlab  # pylint: disable=W7935

from odoo import api, models


class ProjectGitAuth(models.AbstractModel):
    _inherit = "project.git.auth"

    @api.model
    def _connect_gitlab(self, url):
        """Connect to the gitlab instance hosting the given project URL
        and return the gitlab client object.

        :param str url: a project-level URL (e.g. project web_url); the
            instance root is derived from it, and selects the per-instance
            token sysparam (project_gitlab.token.<instance root>)
        """
        url = urljoin(url, "../..")
        token = self._get_token_param("project_gitlab.token." + url)
        return gitlab.Gitlab(url, private_token=token)
