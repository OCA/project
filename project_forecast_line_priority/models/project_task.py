# Copyright 2024 Therp BV
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
        priority = priority or self.priority
        if not priority:
            # This may happen when a portal user
            # is creating a task on portal
            priority = "0"
        selection = self.company_id["forecast_line_priority_%s_selection" % priority]
        if selection == "none":
            return False
        elif selection == "delta":
            return fields.Date.today() + timedelta(
                days=int(self.company_id["forecast_line_priority_%s_delta" % priority])
            )
        elif selection == "date":
            return self.company_id["forecast_line_priority_%s_date" % priority]
        return False
