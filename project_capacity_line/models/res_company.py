# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    capacity_line_granularity = fields.Selection(
        [("day", "Day"), ("week", "Week"), ("month", "Month")],
        default="month",
        help="Periodicity of the capacity lines that will be generated",
    )
    capacity_line_horizon = fields.Integer(
        help="Number of month for the capacity line planning", default=12
    )

    def write(self, values):
        res = super().write(values)
        if "capacity_line_granularity" in values or "capacity_line_horizon" in values:
            for company in self:
                self.env["capacity.line"]._cron_recompute_all(
                    force_company_id=company.id
                )
        return res
