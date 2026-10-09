from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    task_stage_order_ids = fields.One2many(
        "project.task.type.sequence", "project_id", string="Task Stage Order"
    )
    task_stage_order_enabled = fields.Boolean(
        compute="_compute_task_stage_order_enabled"
    )

    def _compute_task_stage_order_enabled(self):
        enabled = self.env.company.task_stage_order_enabled
        for project in self:
            project.task_stage_order_enabled = enabled
