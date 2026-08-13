# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
from urllib.parse import urlparse

from gitlab.exceptions import GitlabJobRetryError

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = "project.project"

    git_project_url = fields.Char(
        string="Git Project URL",
        help="URL of the repository (GitLab or GitHub)",
    )
    git_dev_project_url = fields.Char(
        string="Git Dev Project URL",
        help="URL of the repository (GitLab or GitHub)",
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

        GitHub claims its specific host (the GitHub connection supports
        github.com only, no Enterprise base URL); any other host is
        treated as a GitLab instance (catch-all claim).
        """
        if urlparse(project_url).netloc in ("github.com", "www.github.com"):
            return "github"
        return "gitlab"

    def _get_webhook_url(self):
        return "%s/webhook_gitlab/webhook/" % self.env[
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

    def _create_project_webhook_gitlab(self, project_url):
        gl = self.env["git.auth"]._connect_gitlab(url=project_url)
        gitlab_project = gl.projects.get(self._git_project_path(project_url))
        odoo_url = self._get_webhook_url()
        for hook in gitlab_project.hooks.list():
            if hook.url == odoo_url:
                hook.delete()
        gitlab_project.hooks.create(
            {
                "url": odoo_url,
                "push_events": True,
                "merge_requests_events": True,
                "pipeline_events": True,
                "enable_ssl_verification": True,
                "token": self.env["ir.config_parameter"]
                .sudo()
                .get_param("webhook_gitlab.authorization_token"),
            }
        )

    def _create_project_webhook_github(self, project_url):
        github_client = self.env["git.auth"]._connect_github()
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
                .get_param("webhook_gitlab.authorization_token"),
                "insecure_ssl": "0",
            },
            events=["push", "pull_request"],
            active=True,
        )

    def retry_odoo_sh_deploy_job(self):
        for project in self:
            # The CI job retry is a GitLab-only feature
            if (
                not project.git_project_url
                or self._get_url_platform(project.git_project_url) != "gitlab"
            ):
                continue
            gl = self.env["git.auth"]._connect_gitlab(url=project.git_project_url)
            gitlab_project = gl.projects.get(
                self._git_project_path(project.git_project_url)
            )
            jobs = gitlab_project.jobs.list(scope="success", get_all=False)
            latest_job = False
            for job in filter(lambda x: x.name == "odoo_sh_deploy", jobs):
                if not latest_job or job.created_at > latest_job.created_at:
                    latest_job = job
            if latest_job:
                try:
                    response = latest_job.retry()
                except GitlabJobRetryError as err:
                    raise UserError(
                        _("Job cannot be retried, it is a job in progress")
                    ) from err
                if response.get("web_url"):
                    return {
                        "type": "ir.actions.act_url",
                        "url": response.get("web_url"),
                        "target": "new",
                    }
                raise UserError(_("Job odoo_sh_deploy has been retried"))
            raise UserError(_("No job odoo_sh_deploy found"))
