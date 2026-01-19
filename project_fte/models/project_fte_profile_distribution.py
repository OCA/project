# Copyright 2025 APSL Nagarro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FteProfileDistribution(models.Model):
    _name = "project.fte.profile.distribution"
    _description = "Project FTE Profile Distribution"

    month_line_id = fields.Many2one(
        comodel_name="project.fte.month.line",
        string="Month Line",
        required=True,
        ondelete="cascade",
    )
    role_id = fields.Many2one(
        comodel_name="project.role",
        string="Profile/Role",
        required=True,
    )
    profile_hours = fields.Float()
    profile_hours_percentage = fields.Float(
        string="Percentage",
        compute="_compute_profile_hours_percentage",
        store=True,
        help="Percentage of this profile's hours over the total for the month.",
    )
    profile_price_hour = fields.Float(
        string="Price per Hour",
        store=True,
        help="Price per hour for this profile.",
    )

    @api.depends("profile_hours", "month_line_id.fte_hours")
    def _compute_profile_hours_percentage(self):
        for dist in self:
            total_hours = dist.month_line_id.fte_hours
            if total_hours > 0:
                dist.profile_hours_percentage = (
                    (dist.profile_hours * 100) / total_hours
                ) / 100
            else:
                dist.profile_hours_percentage = 0.0
