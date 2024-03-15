# Copyright 2024 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models

SELECTION_FORECAST_ENDDATE = [
    ("none", "None"),
    ("date", "Date"),
    ("delta", "Delta (in days)"),
]


class ResCompany(models.Model):
    _inherit = "res.company"

    forecast_line_priority_0_date = fields.Date()
    forecast_line_priority_1_date = fields.Date()
    forecast_line_priority_2_date = fields.Date()
    forecast_line_priority_3_date = fields.Date()
    forecast_line_priority_0_delta = fields.Integer()
    forecast_line_priority_1_delta = fields.Integer()
    forecast_line_priority_2_delta = fields.Integer()
    forecast_line_priority_3_delta = fields.Integer()
    forecast_line_priority_0_selection = fields.Selection(
        SELECTION_FORECAST_ENDDATE,
        default="none",
    )
    forecast_line_priority_1_selection = fields.Selection(
        SELECTION_FORECAST_ENDDATE,
        default="none",
    )
    forecast_line_priority_2_selection = fields.Selection(
        SELECTION_FORECAST_ENDDATE,
        default="none",
    )
    forecast_line_priority_3_selection = fields.Selection(
        SELECTION_FORECAST_ENDDATE,
        default="none",
    )
