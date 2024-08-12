# Copyright 2024 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

import odoo.tests.common as common
from odoo import fields


class TestForecastLinePriotity(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.project_task = self.env.ref("project.project_task_1")
        self.company_1 = self.env.company
        self.company_2 = self.env["res.company"].create({"name": "Another Company"})
        self.company_1.write(
            {
                "forecast_line_priority_0_selection": "date",
                "forecast_line_priority_0_date": "2026-01-01",
                "forecast_line_priority_2_selection": "date",
                "forecast_line_priority_2_date": "2024-02-01",
                "forecast_line_priority_3_selection": "delta",
                "forecast_line_priority_3_delta": "15",
            }
        )
        self.company_2.write(
            {
                "forecast_line_priority_2_selection": "delta",
                "forecast_line_priority_2_delta": "7",
                "forecast_line_priority_3_selection": "date",
                "forecast_line_priority_3_date": "2022-01-01",
            }
        )

    @freeze_time("2024-01-01")
    def test_forecast_line_priority(self):
        """Test forecast_date_planned_end vs task priority"""
        # See that relevant date fields are falsy
        task = self.project_task
        self.assertFalse(task.forecast_date_planned_end)
        self.assertFalse(task.date_deadline)
        self.assertEqual(task.priority, "0")
        task.priority = "1"
        # no shift in date due to priority
        self.assertFalse(task.forecast_date_planned_end)
        task.priority = "2"
        # fixed date
        self.assertEqual(
            fields.Date.to_string(task.forecast_date_planned_end), "2024-02-01"
        )
        task.priority = "3"
        # +15 days
        self.assertEqual(
            fields.Date.to_string(task.forecast_date_planned_end), "2024-01-16"
        )
        # set deadline to task
        task.date_deadline = "2025-01-01"
        self.assertEqual(task.forecast_date_planned_end, task.date_deadline)
        # change priority, but nothing changes in forecast end date
        task.priority = "2"
        self.assertEqual(task.forecast_date_planned_end, task.date_deadline)
        # reset date_deadline for original task
        task.date_deadline = False
        # new task, but for a different company
        other_task = task.create(
            {
                "project_id": self.env["project.project"]
                .create({"company_id": self.company_2.id, "name": "other project"})
                .id,
                "priority": "2",
                "name": "other task",
            }
        )
        # launch the server action
        self.env["project.task"]._action_update_forecast_date_end(task + other_task)
        # task is for company_1, and has priority 2,
        # config selection is date, with value "2024-02-01"
        self.assertEqual(
            fields.Date.to_string(task.forecast_date_planned_end), "2024-02-01"
        )
        # other_task is for company_2, and has priority 2,
        # config selection is delta, 7 days, expected value "2024-01-08"
        self.assertEqual(
            fields.Date.to_string(other_task.forecast_date_planned_end), "2024-01-08"
        )
        # set priority for task to False.
        # (possible for portal users)
        task.priority = False
        # system sees priority False as 0, i.e, normal priority
        self.env["project.task"]._action_update_forecast_date_end(task)
        # config selection is date, with value "2026-01-01"
        self.assertEqual(
            fields.Date.to_string(task.forecast_date_planned_end), "2026-01-01"
        )
        # reset task forecast end date
        # to trigger _update_forecast_lines
        tasks = task + other_task
        date_task = task.forecast_date_planned_end
        date_other_task = other_task.forecast_date_planned_end
        # reset
        tasks.write({"forecast_date_planned_end": False})
        tasks._update_forecast_lines()
        self.assertEqual(task.forecast_date_planned_end, date_task)
        self.assertEqual(other_task.forecast_date_planned_end, date_other_task)
