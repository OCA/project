# Copyright 2018, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from urllib.parse import urlparse

from gitlab.exceptions import GitlabJobRetryError

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = "project.project"

    git_project_url = fields.Char(
        string="Git Project URL",
        help="URL of the project in GitLab",
    )
    git_dev_project_url = fields.Char(
        string="Git Dev Project URL",
        help="URL of the project in GitLab",
    )

    def create_project_webhook(self):
        for project in self:
            if project.git_project_url:
                project._create_project_webhook(project.git_project_url)
            if project.git_dev_project_url:
                project._create_project_webhook(project.git_dev_project_url)
        return True

    @api.model
    def _gitlab_project_path(self, project_url):
        """Namespace path of the project as expected by the GitLab API,
        tolerating URLs with a trailing ``.git``."""
        return urlparse(project_url).path.strip("/").removesuffix(".git")

    def _create_project_webhook(self, project_url):
        gl = self.env["git.event"]._connect_gitlab(url=project_url)
        gitlab_project = gl.projects.get(self._gitlab_project_path(project_url))
        hooks = gitlab_project.hooks.list()
        odoo_url = "%s/webhook_gitlab/webhook/" % self.env[
            "ir.config_parameter"
        ].sudo().get_param("web.base.url").strip("/")
        for hook in hooks:
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

    def retry_odoo_sh_deploy_job(self):
        for project in self:
            if not project.git_project_url:
                continue
            gl = self.env["git.event"]._connect_gitlab(url=project.git_project_url)
            gitlab_project = gl.projects.get(
                self._gitlab_project_path(project.git_project_url)
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
