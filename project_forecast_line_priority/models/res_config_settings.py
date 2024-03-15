# Copyright 2024 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    forecast_line_priority_0_date = fields.Date(
        related="company_id.forecast_line_priority_0_date", readonly=False
    )
    forecast_line_priority_1_date = fields.Date(
        related="company_id.forecast_line_priority_1_date", readonly=False
    )
    forecast_line_priority_2_date = fields.Date(
        related="company_id.forecast_line_priority_2_date", readonly=False
    )
    forecast_line_priority_3_date = fields.Date(
        related="company_id.forecast_line_priority_3_date", readonly=False
    )
    forecast_line_priority_0_delta = fields.Integer(
        related="company_id.forecast_line_priority_0_delta", readonly=False
    )
    forecast_line_priority_1_delta = fields.Integer(
        related="company_id.forecast_line_priority_1_delta", readonly=False
    )
    forecast_line_priority_2_delta = fields.Integer(
        related="company_id.forecast_line_priority_2_delta", readonly=False
    )
    forecast_line_priority_3_delta = fields.Integer(
        related="company_id.forecast_line_priority_3_delta", readonly=False
    )
    forecast_line_priority_0_selection = fields.Selection(
        related="company_id.forecast_line_priority_0_selection",
        readonly=False,
        required=True,
    )
    forecast_line_priority_1_selection = fields.Selection(
        related="company_id.forecast_line_priority_1_selection",
        readonly=False,
        required=True,
    )
    forecast_line_priority_2_selection = fields.Selection(
        related="company_id.forecast_line_priority_2_selection",
        readonly=False,
        required=True,
    )
    forecast_line_priority_3_selection = fields.Selection(
        related="company_id.forecast_line_priority_3_selection",
        readonly=False,
        required=True,
    )
