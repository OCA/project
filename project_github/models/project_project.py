# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from urllib.parse import urlparse

from odoo import api, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.model
    def _get_url_platform(self, project_url):
        # Specific claim: the GitHub connection supports github.com
        # only, no Enterprise base URL (claim before super())
        if urlparse(project_url).netloc in ("github.com", "www.github.com"):
            return "github"
        return super()._get_url_platform(project_url)

    def _create_project_webhook_github(self, project_url):
        github_client = self.env["project.git.auth"]._connect_github()
        github_repo = github_client.get_repo(self._git_project_path(project_url))
        odoo_url = self._get_webhook_url()
        for hook in github_repo.get_hooks():
            if hook.config.get("url") == odoo_url:
                hook.delete()
        github_repo.create_hook(
            # The secret signs the payload (X-Hub-Signature-256), which is
            # how the controller authorizes and recognizes GitHub events
            name="web",
            config={
                "url": odoo_url,
                "content_type": "json",
                "secret": self.env["ir.config_parameter"]
                .sudo()
                .get_param("project_git.authorization_token"),
                "insecure_ssl": "0",
            },
            events=["push", "pull_request"],
            active=True,
        )
