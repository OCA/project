# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    monthly_fte_ids = fields.Many2many(
        comodel_name="project.monthly.fte",
        string="Monthly FTEs",
        help="Monthly FTEs associated with the project.",
    )

    def get_rounded_months(self):
        self.ensure_one()
        if not self.date_start or not self.date_end:
            return 0

        year_diff = self.date_end.year - self.date_start.year
        month_diff = self.date_end.month - self.date_start.month
        total_months = year_diff * 12 + month_diff

        day_diff = self.date_end.day - self.date_start.day
        if day_diff >= 0:
            fraction = day_diff / 30.0
        else:
            total_months -= 1
            last_day_prev_month = (self.date_end.replace(day=1) - timedelta(days=1)).day
            fraction = (last_day_prev_month + day_diff) / 30.0

        return total_months + 1 if fraction >= 0 else total_months

    def create_monthly_fte(self):
        self.ensure_one()
        for i in range(self.get_rounded_months()):
            future_date = date.today() + relativedelta(months=i)
            monthly_fte = self.env["project.monthly.fte"].create(
                {
                    "month": future_date.strftime("%m"),
                    "total_fte_hours": self.allocated_hours,
                }
            )
            self.monthly_fte_ids |= monthly_fte
