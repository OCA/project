# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from gitlab.exceptions import GitlabJobRetryError

from odoo import _, api, models
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.model
    def _get_url_platform(self, project_url):
        # Catch-all claim: any host no other platform recognizes is
        # treated as a GitLab instance (claim after super())
        return super()._get_url_platform(project_url) or "gitlab"

    def _create_project_webhook_gitlab(self, project_url):
        gl = self.env["project.git.auth"]._connect_gitlab(url=project_url)
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
                .get_param("project_git.authorization_token"),
            }
        )

    def retry_odoo_sh_deploy_job(self):
        for project in self:
            # The CI job retry is a GitLab-only feature
            if (
                not project.git_project_url
                or self._get_url_platform(project.git_project_url) != "gitlab"
            ):
                continue
            gl = self.env["project.git.auth"]._connect_gitlab(
                url=project.git_project_url
            )
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
