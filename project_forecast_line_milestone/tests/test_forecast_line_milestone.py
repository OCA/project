# Copyright 2024 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestForecastLineMilestone(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.project_task = self.env.ref("project.project_task_1")
        self.project = self.project_task.project_id
        self.project.use_milestones = True
        self.project_milestone = self.env["project.milestone"].create(
            {
                "name": "a milestone",
                "project_id": self.project.id,
                "project_task_ids": [(4, self.project_task.id)],
            }
        )
        self.env.company.write(
            {
                "forecast_line_priority_2_selection": "date",
                "forecast_line_priority_2_date": "2024-02-01",
                "forecast_line_priority_3_selection": "delta",
                "forecast_line_priority_3_delta": "15",
            }
        )

    def test_forecast_end_milestone(self):
        """Test forecast_date_planned_end vs project_milestone"""
        task = self.project_task
        milestone = self.project_milestone
        # See that relevant date fields are falsy
        self.assertFalse(task.forecast_date_planned_end)
        self.assertFalse(task.date_deadline)
        self.assertFalse(milestone.target_date)
        # Set deadline for task
        task.date_deadline = "2022-01-01"
        # Date fields are equal
        self.assertEqual(task.forecast_date_planned_end, task.date_deadline)
        # Set target_date for milestone
        milestone.target_date = "2050-01-01"
        # forecast end is now milestone end
        self.assertEqual(task.forecast_date_planned_end, milestone.target_date)
        # Reset deadline and change priority
        task.date_deadline = False
        task.priority = "2"
        # nothing changes
        self.assertEqual(task.forecast_date_planned_end, milestone.target_date)
