# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    forecast_line_granularity = fields.Selection(
        [("day", "Day"), ("week", "Week"), ("month", "Month")],
        default="month",
        help="Periodicity of the forecast that will be generated",
    )
    forecast_line_horizon = fields.Integer(
        help="Number of month for the forecast planning", default=12
    )
    forecast_consumption_states = fields.Selection(
        selection=[
            ("confirmed", "Compute consolidated forecast for lines of type confirmed"),
            (
                "forecast_confirmed",
                "Include lines of type forecast in consolidated forecast computation",
            ),
        ],
        string="Consumption state rules",
        help="For instance, holidays requests and sales quotation lines"
        "create lines of type forecast and won't be taken into account"
        "during consolidated forecast computation, whereas tasks for project"
        "which are in a running state create lines with type confirmed"
        "and will be used to compute consolidated forecast.",
        default="confirmed",
    )

    def write(self, values):
        res = super().write(values)
        if "forecast_line_granularity" in values or "forecast_line_horizon" in values:
            for company in self:
                self.env["forecast.line"]._cron_recompute_all(
                    force_company_id=company.id
                )
        return res
