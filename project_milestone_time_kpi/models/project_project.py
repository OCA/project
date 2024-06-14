# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class Project(models.Model):
    _inherit = "project.project"

    total_estimated_hours = fields.Float(
        "Total Estimated Hours", compute="_compute_total_hours", store=True
    )
    total_spent_hours = fields.Float(
        "Total Spent Hours", compute="_compute_total_hours", store=True
    )
    remaining_estimated_hours = fields.Float(
        "Remaining Estimated Hours",
        compute="_compute_remaining_estimated_hours", store=True
    )
    total_remaining_hours = fields.Float(
        "Total Remaining Work", compute="_compute_remaining_hours", store=True
    )

    @api.depends("milestone_ids", "milestone_ids.estimated_hours",
                 "milestone_ids.total_hours")
    def _compute_total_hours(self):
        for project in self:
            project.total_estimated_hours = sum(
                project.milestone_ids.mapped("estimated_hours"))
            project.total_spent_hours = sum(
                project.milestone_ids.mapped("total_hours"))

    @api.depends("total_estimated_hours", "total_spent_hours")
    def _compute_remaining_estimated_hours(self):
        for project in self:
            project.remaining_estimated_hours = \
                project.total_estimated_hours - project.total_spent_hours

    @api.depends("task_ids", "task_ids.remaining_hours")
    def _compute_remaining_hours(self):
        for project in self:
            project.total_remaining_hours = sum(
                project.task_ids.mapped("remaining_hours"))
