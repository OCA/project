# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectMonthlyFTE(models.Model):
    _name = "project.monthly.fte"
    _description = "Project Monthly FTE"

    month = fields.Selection(
        [
            ("01", "January"),
            ("02", "February"),
            ("03", "March"),
            ("04", "April"),
            ("05", "May"),
            ("06", "June"),
            ("07", "July"),
            ("08", "August"),
            ("09", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ]
    )
    total_fte_hours = fields.Float(
        string="Total FTE Hours",
        required=True,
        help="Total FTE hours for the project in the month.",
    )
