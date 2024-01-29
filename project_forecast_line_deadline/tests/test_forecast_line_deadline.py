# Copyright 2024 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests.common as common
from odoo import fields


class TestForecastLineDeadline(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.project_task = self.env.ref("project.project_task_1")

    def test_forecast_end_deadline(self):
        """Test forecast_date_planned_end vs date_deadline"""
        task = self.project_task
        # See that relevant date fields are falsy
        self.assertFalse(task.forecast_date_planned_end)
        self.assertFalse(task.date_deadline)
        # Set deadline for task
        task.date_deadline = "2022-01-01"
        # Date fields are equal
        self.assertEqual(task.forecast_date_planned_end, task.date_deadline)
        # Set forecast_date_deadline manually
        task.forecast_date_planned_end = "2022-02-01"
        # Dates are not the same anymore
        self.assertNotEqual(task.forecast_date_planned_end, task.date_deadline)
        self.assertEqual(
            fields.Date.to_string(task.forecast_date_planned_end), "2022-02-01"
        )
        self.assertEqual(fields.Date.to_string(task.date_deadline), "2022-01-01")
        # Reset both date fields to False
        task.date_deadline = False
        self.assertFalse(task.forecast_date_planned_end)
