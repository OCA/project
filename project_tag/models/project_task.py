# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    tags_required = fields.Boolean("Tags Required", related="project_id.tags_required")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get("default_parent_id", False):
            parent_task = self.browse(self.env.context.get("default_parent_id"))

            if parent_task.tag_ids:
                res.update(
                    {
                        "tag_ids": [(6, 0, parent_task.tag_ids.ids)],
                    }
                )
        return res
