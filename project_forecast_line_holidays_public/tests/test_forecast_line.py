# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo import fields

from odoo.addons.project_forecast_line.tests import test_forecast_line


class PublicHolidaysForecastTest(test_forecast_line.BaseForecastLineTest):
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
        self.env["hr.holidays.public"].create(
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
