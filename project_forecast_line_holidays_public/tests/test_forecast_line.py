# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date

from freezegun import freeze_time

from odoo import fields

from odoo.addons.project_forecast_line.tests import test_forecast_line


class PublicHolidaysForecastTest(test_forecast_line.BaseForecastRoleTest):
    @classmethod
    @freeze_time("2022-01-01")
    def setUpClass(cls):
        super().setUpClass()
        # for this test, we use a daily granularity
        cls.env.company.write(
            {
                "forecast_line_granularity": "month",
                "forecast_line_horizon": 1,  # months
            }
        )

    @freeze_time("2022-04-01")
    def test_forecast_with_public_holidays(self):
        self.env["calendar.public.holiday"].create(
            {
                "year": 2022,
                "line_ids": [
                    fields.Command.create(
                        {"date": "2022-04-18", "name": "Easter Monday"}
                    )
                ],
            }
        )
        lines = self.env["forecast.line"].search(
            [
                ("employee_id", "=", self.employee_dev.id),
                ("forecast_role_id", "=", self.role_developer.id),
                ("res_model", "=", "hr.employee.forecast.role"),
            ]
        )
        self.assertEqual(len(lines), 1)  # 1 month horizon
        self.assertEqual(
            lines.mapped("forecast_hours"),
            # number of days April, minus easter
            [(21.0 - 1) * 8],
        )

    @freeze_time("2022-04-01")
    def test_number_of_hours_excludes_holidays_without_cron_context(self):
        # regression test: _number_of_hours used to only exclude public
        # holidays when called with an "exclude_public_holidays" context
        # key, which only _cron_recompute_all() ever set. Every real-time
        # recompute path (hr.leave, sale.order.line, project.task,
        # hr.employee.forecast.role...) calls it with no such context, so
        # public holidays were silently ignored outside the nightly cron.
        self.env["calendar.public.holiday"].create(
            {
                "year": 2022,
                "line_ids": [
                    fields.Command.create(
                        {"date": "2022-04-18", "name": "Easter Monday"}
                    )
                ],
            }
        )
        resource = self.employee_dev.resource_id
        calendar = self.employee_dev.resource_calendar_id
        hours = self.env["forecast.line"]._number_of_hours(
            date(2022, 4, 1), date(2022, 5, 1), resource, calendar
        )
        # number of days in April, minus easter
        self.assertEqual(hours, (21.0 - 1) * 8)
