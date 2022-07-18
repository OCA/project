# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        recs._update_forecast_lines()
        return recs

    def write(self, values):
        res = super().write(values)
        self._update_forecast_lines()
        return res

    def _update_forecast_lines(self):
        resources = self.mapped("resource_id")
        if resources:
            employees = self.env["hr.employee"].search([("id", "in", resources.ids)])
        else:
            employees = self.env["hr.employee"].search(
                [("company_id", "in", self.mapped("company_id").ids)]
            )
        roles = self.env["hr.employee.forecast.role"].search(
            [("employee_id", "in", employees.ids)]
        )
        roles._update_forecast_lines()
