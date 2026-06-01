# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from .test_forecast_line import BaseForecastRoleTest


class TestHrLeave(BaseForecastRoleTest):
    @freeze_time("2022-01-01 12:00:00")
    def test_update_forecast_lines_skips_employee_without_main_role(self):
        """When an employee has no main_role_id, _update_forecast_lines
        must skip the leave (continue) and NOT create any forecast lines
        for it.
        """
        # Create an employee with NO forecast role assignments
        employee_no_role = self.HrEmployee.create({"name": "No Role Employee"})
        user_no_role = self.ResUsers.create(
            {"name": "No Role User", "login": "norole@example.com"}
        )
        employee_no_role.user_id = user_no_role.id
        self.env.flush_all()

        # Confirm the employee has no main_role_id
        self.assertFalse(
            employee_no_role.main_role_id,
            "Employee must have no main_role_id for this test",
        )

        # Create an HR leave for this employee
        leave_type = self.env["hr.leave.type"].create(
            {
                "name": "Test Leave Type",
                "requires_allocation": "no",
            }
        )
        leave = (
            self.env["hr.leave"]
            .with_user(user_no_role)
            .create(
                {
                    "name": "Sick Day",
                    "holiday_status_id": leave_type.id,
                    "date_from": "2022-03-14 08:00:00",
                    "date_to": "2022-03-15 17:00:00",
                    "employee_id": employee_no_role.id,
                }
            )
        )
        self.env.flush_all()

        # No forecast lines should be created for this leave
        forecast_lines = self.ForecastLine.search(
            [
                ("res_model", "=", "hr.leave"),
                ("res_id", "=", leave.id),
            ]
        )
        self.assertFalse(
            forecast_lines,
            "No forecast lines must be created when the employee "
            "has no main_role_id",
        )

    @freeze_time("2022-01-01 12:00:00")
    def test_update_forecast_lines_creates_lines_for_employee_with_role(self):
        """When an employee has a main_role_id and the leave state is not
        'validate' or 'refuse', _update_forecast_lines must create
        forecast lines for the leave.
        """
        # employee_consultant has a role via consult_employee_forecast_role
        self.assertTrue(
            self.employee_consultant.main_role_id,
            "Employee must have a main_role_id for this test",
        )

        leave_type = self.env["hr.leave.type"].create(
            {
                "name": "Test Leave Type 2",
                "requires_allocation": "no",
            }
        )
        leave = (
            self.env["hr.leave"]
            .with_user(self.user_consultant)
            .create(
                {
                    "name": "Vacation",
                    "holiday_status_id": leave_type.id,
                    "date_from": "2022-03-14 08:00:00",
                    "date_to": "2022-03-15 17:00:00",
                    "employee_id": self.employee_consultant.id,
                }
            )
        )
        self.env.flush_all()

        # Forecast lines SHOULD be created for this leave
        forecast_lines = self.ForecastLine.search(
            [
                ("res_model", "=", "hr.leave"),
                ("res_id", "=", leave.id),
            ]
        )
        self.assertTrue(
            forecast_lines,
            "Forecast lines must be created when the employee has a "
            "main_role_id and leave is not validated/refused",
        )
        self.assertEqual(
            forecast_lines.forecast_role_id,
            self.role_consultant,
            "Forecast line must use the employee's main_role_id",
        )
