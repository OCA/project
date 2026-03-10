from freezegun import freeze_time

from .test_forecast_line import BaseForecastRoleTest


# ======================================================================
# Tests for forecast.line.mixin._get_forecast_lines
# ======================================================================
class TestForecastLineMixin(BaseForecastRoleTest):
    def test_get_forecast_lines(self):
        # Test retrieving lines without an extra domain
        lines = self.ProjectTasks._get_forecast_lines()
        # Assertions
        self.assertIn(
            self.forecast_line_one,
            lines,
            "Should find the linked forecast line",  # noqa:E501
        )
        self.assertNotIn(
            self.forecast_line_other,
            lines,
            "Should not find lines linked to other IDs",  # noqa:E501
        )
        self.assertEqual(len(lines), 2)

        # Test retrieving lines with an extra domain
        lines = self.ProjectTasks._get_forecast_lines(
            domain=[("forecast_role_id", "=", 1)]
        )
        self.assertIn(
            self.forecast_line_one,
            lines,
            "This should fetch line 2 and not Line 1",  # noqa:E501
        )
        self.assertEqual(len(lines), 1)

    @freeze_time("2022-02-14 12:00:00")
    def _make_task_with_lines(self, name, hours=8):
        """Helper: create a qualifying task that already has a forecast line."""
        project = self.ProjectProject.create({"name": f"MixinProject-{name}"})
        project.stage_id = self.env.ref("project.project_project_stage_1")
        task = self.ProjectTask.create(
            {
                "name": name,
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "forecast_date_planned_start": "2022-02-14",
                "forecast_date_planned_end": "2022-02-14",
                "allocated_hours": hours,
                "remaining_hours": hours,
            }
        )
        task.user_ids = self.user_consultant
        task._update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()
        return task

    def test_get_forecast_lines_ensure_one_raises_on_multi_record(self):
        """ensure_one() must raise ValueError when the method is called
        on a recordset that contains more than one record."""
        with freeze_time("2022-02-14 12:00:00"):
            task_a = self._make_task_with_lines("MixinTaskA")
            task_b = self._make_task_with_lines("MixinTaskB")

        multi = task_a | task_b
        self.assertEqual(len(multi), 2)
        with self.assertRaises(ValueError):
            multi._get_forecast_lines()
