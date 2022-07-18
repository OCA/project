# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo import fields

from odoo.addons.project_capacity_line.tests import test_capacity_line


class PublicHolidaysCapacityTest(test_capacity_line.BaseCapacityLineTest):
    @classmethod
    @freeze_time("2022-01-01")
    def setUpClass(cls):
        super().setUpClass()
        # for this test, we use a daily granularity
        cls.env.company.write(
            {
                "capacity_line_granularity": "month",
                "capacity_line_horizon": 1,  # months
            }
        )

    @freeze_time("2022-04-01")
    def test_capacity_with_public_holidays(self):
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
        lines = self.env["capacity.line"].search(
            [
                ("employee_id", "=", self.employee_dev.id),
                ("capacity_role_id", "=", self.role_developer.id),
                ("res_model", "=", "hr.employee.capacity.role"),
            ]
        )
        self.assertEqual(len(lines), 1)  # 1 month horizon
        self.assertEqual(
            lines.mapped("capacity_hours"),
            # number of days April, minus easter
            [(21.0 - 1) * 8],
        )
