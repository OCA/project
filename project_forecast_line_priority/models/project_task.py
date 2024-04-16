# Copyright 2024 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _forecast_date_planned_end_depends_list(self):
        """Returns a list of fields to trigger recomputation"""
        return super()._forecast_date_planned_end_depends_list() + ["priority"]

    @api.depends(_forecast_date_planned_end_depends_list)
    def _compute_forecast_date_planned_end(self):
        """Override method to use recompute based on priority"""
        res = super()._compute_forecast_date_planned_end()
        for task in self:
            task.forecast_date_planned_end = (
                task._get_forecast_date_planned() or task.forecast_date_planned_end
            )
        return res

    def _update_forecast_lines(self):
        """Override cron method and inject forecast date recomputation"""
        for task in self:
            forecast_date_planned_end = task._get_forecast_date_planned()
            if not forecast_date_planned_end:
                continue
            task.forecast_date_planned_end = forecast_date_planned_end
        return super()._update_forecast_lines()

    @api.model
    def _action_update_forecast_date_end(self, tasks):
        for task in tasks:
            new_forecast_date_planned_end = task._get_forecast_date_planned()
            if not new_forecast_date_planned_end:
                continue
            task.write(
                {
                    "forecast_date_planned_end": new_forecast_date_planned_end,
                }
            )

    def _get_forecast_date_planned(self, priority=None):
        """Update forecast date end based on priority"""
        self.ensure_one()
        if self.date_deadline:
            return False
        priority = priority or self.priority or "0"
        selection = getattr(
            self.company_id, "forecast_line_priority_%s_selection" % priority, None
        )
        if selection == "delta":
            days = getattr(
                self.company_id, "forecast_line_priority_%s_delta" % priority, 0
            )
            if days:
                return fields.Date.today() + timedelta(int(days))
        if selection == "date":
            return getattr(
                self.company_id, "forecast_line_priority_%s_date" % priority, False
            )
        return False
