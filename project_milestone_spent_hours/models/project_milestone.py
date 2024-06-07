# © 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    total_hours = fields.Float(
        compute="_compute_total_hours",
        string="Total Hours",
        compute_sudo=True,
        store=True,
    )

    @api.depends(
        "project_task_ids",
        "project_task_ids.active",
        "project_task_ids.milestone_id",
        "project_task_ids.timesheet_ids",
        "project_task_ids.timesheet_ids.unit_amount",
        "active",
    )
    def _compute_total_hours(self):
        for record in self:
            total_hours = 0.0
            if record.active:
                total_hours = sum(
                    record.project_task_ids.filtered(lambda milestone: milestone.active)
                    .mapped("timesheet_ids")
                    .mapped("unit_amount")
                )
            record.total_hours = total_hours
