# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class ProjectTaskTypeDeleteWizard(models.TransientModel):
    _inherit = "project.task.type.delete.wizard"

    @api.depends("project_ids")
    def _compute_tasks_count(self):
        project_id = self.env.context.get("default_project_id")
        if not project_id or not self.env.company.task_stage_order_enabled:
            return super()._compute_tasks_count()
        for wizard in self:
            wizard.tasks_count = self.env["project.task"].search_count(
                [
                    ("stage_id", "in", wizard.stage_ids.ids),
                    ("project_id", "=", project_id),
                ]
            )
