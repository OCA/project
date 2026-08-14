# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
from urllib.parse import urlparse

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = "project.project"

    git_project_url = fields.Char(
        string="Git Project URL",
        help="URL of the repository on the git hosting platform",
    )
    git_dev_project_url = fields.Char(
        string="Git Dev Project URL",
        help="URL of the repository on the git hosting platform",
    )

    def create_project_webhook(self):
        for project in self:
            if project.git_project_url:
                project._create_project_webhook(project.git_project_url)
            if project.git_dev_project_url:
                project._create_project_webhook(project.git_dev_project_url)
        return True

    @api.model
    def _git_project_path(self, project_url):
        """Namespace path of the repository as expected by the platform
        API, tolerating URLs with a trailing ``.git``."""
        return urlparse(project_url).path.strip("/").removesuffix(".git")

    @api.model
    def _get_url_platform(self, project_url):
        """Platform hosting the given repository URL.

        Each platform bridge claims its URLs along the detection chain:
        specific claims come before super() (e.g. GitHub recognizing its
        own host), catch-all claims after it (e.g. GitLab accepting any
        self-hosted instance). Without any bridge no platform is
        recognized.
        """
        return ""

    def _get_webhook_url(self):
        return "%s/project_git/webhook/" % self.env[
            "ir.config_parameter"
        ].sudo().get_param("web.base.url").strip("/")

    def _create_project_webhook(self, project_url):
        platform = self._get_url_platform(project_url)
        if not hasattr(self, "_create_project_webhook_%s" % platform):
            _logger.warning(
                "No webhook deployment implementation for platform %r", platform
            )
            return
        getattr(self, "_create_project_webhook_%s" % platform)(project_url)
