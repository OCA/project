# Copyright 2017 Specialty Medical Drugstore
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from urllib.parse import urlparse

from odoo import _, api, exceptions, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    pr_uri = fields.Char(string="PR URI", tracking=True)

    pr_required_states = fields.Many2many(related="project_id.pr_required_states")

    @api.constrains("pr_uri", "stage_id", "project_id")
    def _check_pr_uri_required(self):
        for task in self:
            stages_pr_req = task.project_id.pr_required_states
            is_stage_pr_req = task.stage_id in stages_pr_req
            if not task.pr_uri and stages_pr_req and is_stage_pr_req:
                raise exceptions.ValidationError(
                    _(
                        "Please add the URI for the pull request "
                        "before moving the task to this stage."
                    )
                )

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        for i, v in enumerate(args):
            if "pr_uri" in v and isinstance(v[2], str):
                url = self.clean_url(v[2])
                query = list(args[i])
                query[-1] = url
                args[i] = tuple(query)
        return super()._search(args, offset, limit, order, count, access_rights_uid)

    @staticmethod
    def clean_url(url):
        """
        Remove scheme, params, query from URL

        Takes only the first four elements of the path, since it should always be:
        org/repo/pull/pr_number

        Anything else is not required and can only be misleading during the search
        """
        url = urlparse(url)
        url_path = "/".join(url.path.split("/")[:5])
        return url.netloc + url_path
