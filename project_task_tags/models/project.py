# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    allowed_tag_ids = fields.Many2many("project.tags", compute="_compute_task_tags")

    @api.depends("project_id", "project_id.tag_ids")
    def _compute_task_tags(self):
        # compute available tags based on project_id
        for rec in self:
            rec.allowed_tag_ids = False
            if rec.project_id and rec.project_id.tag_ids:
                rec.write({"allowed_tag_ids": rec.project_id.tag_ids.mapped("id")})
            else:
                # if there is no project or no tags on proj, we want to have all tags available
                all_tags = self.env["project.tags"].search([])
                rec.write({"allowed_tag_ids": all_tags.mapped("id")})
