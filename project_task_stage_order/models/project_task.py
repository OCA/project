# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        stages = super()._read_group_stage_ids(stages, domain)
        if not self.env.company.task_stage_order_enabled:
            return stages
        project_id = self.env.context.get("default_project_id")
        if project_id:
            stages = (
                self.env["project.task.type.sequence"]
                .search(
                    [
                        ("project_id", "=", project_id),
                        ("stage_id", "in", stages.ids),
                    ]
                )
                .mapped("stage_id")
            )
        return stages
