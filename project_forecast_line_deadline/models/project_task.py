# Copyright 2024 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    # Make forecast end date computable and stored
    forecast_date_planned_end = fields.Date(
        compute="_compute_forecast_date_planned_end", readonly=False, store=True
    )

    def _forecast_date_planned_end_depends_list(self):
        """Returns a list of fields to trigger recomputation"""
        return ["date_deadline"]

    @api.depends(_forecast_date_planned_end_depends_list)
    def _compute_forecast_date_planned_end(self):
        """Set forecast end to be equal with date deadline"""
        for task in self:
            task.forecast_date_planned_end = task.date_deadline
