# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    task_stage_order_ids = fields.One2many(
        "project.task.type.sequence", "project_id", string="Task Stage Order"
    )
    task_stage_order_enabled = fields.Boolean(
        compute="_compute_task_stage_order_enabled"
    )

    @api.depends_context("company")
    def _compute_task_stage_order_enabled(self):
        enabled = self.env.company.task_stage_order_enabled
        for project in self:
            project.task_stage_order_enabled = enabled

    def write(self, values):
        old_stages = (
            self.type_ids if "type_ids" in values else self.env["project.task.type"]
        )
        result = super().write(values)
        if "type_ids" in values and self.env.company.task_stage_order_enabled:
            (old_stages | self.type_ids)._sync_task_stage_order()
        return result

    @api.model_create_multi
    def create(self, values_list):
        projects = super().create(values_list)
        if self.env.company.task_stage_order_enabled:
            projects.type_ids._sync_task_stage_order()
        return projects
