from odoo import api, fields, models


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    execution = fields.Integer(compute="_compute_execution")
    dedication = fields.Integer(compute="_compute_dedication")

    @api.depends("task_ids")
    def _compute_execution(self):
        for milestone in self:
            executed_tasks = milestone.task_ids.filtered("stage_id.fold")

            total_planned_hours = sum(milestone.task_ids.mapped("planned_hours"))
            total_excuted_hours = sum(executed_tasks.mapped("planned_hours"))

            if total_excuted_hours and total_planned_hours:
                milestone.execution = total_excuted_hours * 100 / total_planned_hours
            else:
                milestone.execution = 0

    @api.depends("task_ids")
    def _compute_dedication(self):
        for milestone in self:
            total_planned_hours = sum(milestone.task_ids.mapped("planned_hours"))
            total_dedicated_hours = sum(milestone.task_ids.mapped("effective_hours"))

            if total_dedicated_hours and total_planned_hours:
                milestone.dedication = total_dedicated_hours * 100 / total_planned_hours
            else:
                milestone.dedication = 0
