# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ForecastLine(models.Model):
    _inherit = "forecast.line"

    def _number_of_hours(self, date_from, date_to, resource, calendar, *args, **kwargs):
        if not resource:
            return super()._number_of_hours(
                date_from, date_to, resource, calendar, *args, **kwargs
            )
        employee = resource.employee_id[:1]
        context = {"exclude_public_holidays": True}
        if employee:
            context["employee_id"] = employee.id
        return super()._number_of_hours(
            date_from,
            date_to,
            resource,
            calendar.with_context(**context),
            *args,
            **kwargs,
        )

    def _cron_recompute_all(self, force_company_id=None, force_delete=False):
        self = self.with_context(exclude_public_holidays=True)
        return super()._cron_recompute_all(force_company_id, force_delete)
