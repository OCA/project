# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.tests import Form, TransactionCase, tagged


@tagged("-at_install", "post_install")
class BaseForecastRoleTest(TransactionCase):
    @classmethod
    @freeze_time("2022-01-01")
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.ResUsers = cls.env["res.users"]
        cls.ResPartner = cls.env["res.partner"]
        cls.HrEmployee = cls.env["hr.employee"]
        cls.HrEmployeeForecastRole = cls.env["hr.employee.forecast.role"]
        cls.ForecastRole = cls.env["forecast.role"]
        cls.ForecastLine = cls.env["forecast.line"]
        cls.role_model = cls.HrEmployeeForecastRole._name
        cls.ProductProduct = cls.env["product.product"]
        cls.ProjectProject = cls.env["project.project"]
        cls.ProjectTask = cls.env["project.task"]
        cls.env.company.write(
            {
                "forecast_line_granularity": "month",
                "forecast_line_horizon": 6,  # months
            }
        )
        cls.role_developer = cls.ForecastRole.create({"name": "developer"})
        cls.role_consultant = cls.ForecastRole.create({"name": "consultant"})
        cls.role_pm = cls.ForecastRole.create({"name": "project manager"})
        cls.company = cls.env["res.company"].search([("id", "=", "1")])
        cls.employee_dev = cls.HrEmployee.create({"name": "John Dev"})
        cls.user_consultant = cls.ResUsers.create(
            {"name": "John Consultant", "login": "jc@example.com"}
        )
        cls.employee_consultant = cls.HrEmployee.create(
            {"name": "John Consultant", "user_id": cls.user_consultant.id}
        )
        cls.user_pm = cls.ResUsers.create(
            {"name": "John Peem", "login": "jp@example.com"}
        )
        cls.employee_pm = cls.HrEmployee.create(
            {"name": "John Peem", "user_id": cls.user_pm.id}
        )
        cls.dev_employee_forecast_role = cls.HrEmployeeForecastRole.create(
            {
                "employee_id": cls.employee_dev.id,
                "role_id": cls.role_developer.id,
                "date_start": "2022-01-01",
                "sequence": 1,
            }
        )
        cls.consult_employee_forecast_role = cls.HrEmployeeForecastRole.create(
            {
                "employee_id": cls.employee_consultant.id,
                "role_id": cls.role_consultant.id,
                "date_start": "2022-01-01",
                "sequence": 1,
            }
        )
        cls.pm_employee_forecast_role = cls.HrEmployeeForecastRole.create(
            {
                "employee_id": cls.employee_pm.id,
                "role_id": cls.role_pm.id,
                "date_start": "2022-01-01",
                "sequence": 1,
            }
        )

        cls.product_dev_tm = cls.ProductProduct.create(
            {
                "name": "development time and material",
                "type": "service",
                "service_tracking": "task_in_project",
                "list_price": 95,
                "standard_price": 75,
                "forecast_role_id": cls.role_developer.id,
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
                "uom_po_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )
        cls.product_consultant_tm = cls.ProductProduct.create(
            {
                "name": "consultant time and material",
                "type": "service",
                "service_tracking": "task_in_project",
                "list_price": 100,
                "standard_price": 80,
                "forecast_role_id": cls.role_consultant.id,
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
                "uom_po_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )

        cls.product_pm_tm = cls.ProductProduct.create(
            {
                "name": "pm time and material",
                "type": "service",
                "service_tracking": "task_in_project",
                "list_price": 120,
                "standard_price": 100,
                "forecast_role_id": cls.role_pm.id,
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
                "uom_po_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )
        cls.customer = cls.ResPartner.create({"name": "Some Customer"})
        cls.user_root = cls.env.ref("base.user_root")

        cls.project = cls.ProjectProject.create(
            {
                "name": "Test Coverage Project",
                "allow_billable": True,
            }
        )
        cls.ProjectTasks = cls.ProjectTask.create(
            {
                "name": "test",
                "project_id": cls.project.id,
            }
        )
        cls.forecast_line_one = cls.ForecastLine.create(
            {
                "company_id": 1,
                "type": "forecast",
                "forecast_role_id": 1,
                "date_from": date.today(),
                "date_to": date.today() + relativedelta(day=1),
                "consolidated_forecast": 10.0,
                "confirmed_consolidated_forecast": 10.0,
                "res_model": cls.ProjectTasks._name,
                "res_id": cls.ProjectTasks.id,
                "task_id": cls.ProjectTasks.id,
                "name": "Line 1",
            }
        )
        cls.forecast_line_two = cls.ForecastLine.create(
            {
                "company_id": 1,
                "type": "forecast",
                "forecast_role_id": 2,
                "date_from": date.today(),
                "date_to": date.today() + relativedelta(day=1),
                "consolidated_forecast": 20.0,
                "confirmed_consolidated_forecast": 20.0,
                "res_model": cls.ProjectTasks._name,
                "res_id": cls.ProjectTasks.id,
                "name": "Line 2",
            }
        )
        cls.forecast_line_other = cls.ForecastLine.create(
            {
                "company_id": 1,
                "type": "forecast",
                "forecast_role_id": 3,
                "date_from": date.today(),
                "date_to": date.today() + relativedelta(day=1),
                "consolidated_forecast": 10.0,
                "confirmed_consolidated_forecast": 10.0,
                "res_model": cls.ProjectTasks._name,
                "res_id": 6565,
                "name": "Other Line",
            }
        )
        # Stage with forecast enabled
        cls.stage_forecast = cls.env["project.project.stage"].create(
            {
                "name": "Execution",
                "forecast_line_type": "forecast",
            }
        )


class TestForecastRoleEmployee(BaseForecastRoleTest):
    def test_employee_main_role(self):
        self.HrEmployeeForecastRole.create(
            {
                "employee_id": self.employee_consultant.id,
                "role_id": self.role_developer.id,
                "date_start": "2021-01-01",
                "date_end": "2021-12-31",
                "sequence": 0,
            }
        )
        self.assertEqual(self.employee_consultant.main_role_id, self.role_consultant)

    def test_employee_job_role(self):
        job = self.env["hr.job"].create(
            {"name": "Developer", "role_id": self.role_developer.id}
        )
        employee = self.env["hr.employee"].create(
            {"name": "John Dev", "job_id": job.id}
        )
        self.assertEqual(employee.main_role_id, self.role_developer)
        self.assertEqual(len(employee.role_ids), 1)
        self.assertEqual(employee.role_ids.rate, 100)

    def test_employee_job_role_change(self):
        job1 = self.env["hr.job"].create(
            {"name": "Consultant", "role_id": self.role_consultant.id}
        )
        job2 = self.env["hr.job"].create(
            {"name": "Developer", "role_id": self.role_developer.id}
        )
        employee = self.env["hr.employee"].create(
            {"name": "John Dev", "job_id": job2.id}
        )
        employee.job_id = job1
        self.assertEqual(employee.main_role_id, self.role_consultant)
        self.assertEqual(len(employee.role_ids), 1)
        self.assertEqual(employee.role_ids.rate, 100)

    @freeze_time("2022-01-01")
    def test_employee_forecast(self):
        lines = self.ForecastLine.search(
            [
                ("employee_id", "=", self.employee_consultant.id),
                ("forecast_role_id", "=", self.role_consultant.id),
                ("res_model", "=", self.role_model),
            ]
        )
        self.assertEqual(len(lines), 6)  # 6 months horizon
        self.assertEqual(
            lines.mapped("forecast_hours"),
            # number of working days in the first 6 months of 2022, no vacations
            [21.0 * 8, 20.0 * 8, 23.0 * 8, 21.0 * 8, 22.0 * 8, 22.0 * 8],
        )
        res_ids = self.consult_employee_forecast_role.ids
        self.consult_employee_forecast_role.unlink()
        to_remove_lines = self.ForecastLine.search(
            [("res_id", "in", res_ids), ("res_model", "=", "hr.employee.forecast.role")]
        )
        self.assertFalse(to_remove_lines.exists())

    @freeze_time("2022-01-01")
    def test_employee_forecast_unlink(self):
        roles = self.employee_consultant.role_ids
        lines = self.ForecastLine.search(
            [
                ("employee_id", "=", self.employee_consultant.id),
                ("forecast_role_id", "=", self.role_consultant.id),
                ("res_model", "=", self.role_model),
            ]
        )
        roles.unlink()
        self.assertFalse(lines.exists())

    @freeze_time("2022-01-01")
    def test_employee_forecast_change_roles(self):
        # employee becomes 50% consultant, 50% PM on Feb 1st
        roles = self.employee_consultant.role_ids
        roles.write({"date_end": "2022-01-31"})
        self.env.flush_all()
        lines = self.ForecastLine.search(
            [
                ("employee_id", "=", self.employee_consultant.id),
                ("forecast_role_id", "=", self.role_consultant.id),
                ("res_model", "=", self.role_model),
            ]
        )
        self.assertEqual(len(lines), 1)  # 100% consultant role now ends on 31/01
        self.assertEqual(lines.forecast_hours, 21.0 * 8)
        self.HrEmployeeForecastRole.create(
            [
                {
                    "employee_id": self.employee_consultant.id,
                    "role_id": self.role_consultant.id,
                    "date_start": "2022-02-01",
                    "sequence": 1,
                    "rate": 50,
                },
                {
                    "employee_id": self.employee_consultant.id,
                    "role_id": self.role_pm.id,
                    "date_start": "2022-02-01",
                    "sequence": 2,
                    "rate": 50,
                },
            ]
        )
        self.env.flush_all()
        lines = self.ForecastLine.search(
            [
                ("employee_id", "=", self.employee_consultant.id),
                ("forecast_role_id", "=", self.role_consultant.id),
            ]
        )
        self.assertEqual(len(lines), 6)  # 6 months horizon
        self.assertEqual(
            lines.mapped("forecast_hours"),
            # number of days in the first 6 months of 2022
            [
                21.0 * 8,
                20.0 * 8 / 2,
                23.0 * 8 / 2,
                21.0 * 8 / 2,
                22.0 * 8 / 2,
                22.0 * 8 / 2,
            ],
        )
        res_ids = self.consult_employee_forecast_role.ids
        self.consult_employee_forecast_role.unlink()
        to_remove_lines = self.ForecastLine.search(
            [("res_id", "in", res_ids), ("res_model", "=", "hr.employee.forecast.role")]
        )
        self.assertFalse(to_remove_lines.exists())

    @freeze_time("2022-01-01 12:00:00")
    def test_forecast_with_calendar(self):
        calendar = self.employee_dev.resource_calendar_id
        self.env["resource.calendar.leaves"].create(
            {
                "name": "Easter monday",
                "calendar_id": calendar.id,
                "date_from": "2022-04-18 00:00:00",
                "date_to": "2022-04-19 00:00:00",  # Easter
                "time_type": "leave",
            }
        )
        self.env.flush_all()
        lines = self.ForecastLine.search(
            [
                ("employee_id", "=", self.employee_dev.id),
                ("forecast_role_id", "=", self.role_developer.id),
                ("res_model", "=", self.role_model),
            ]
        )
        self.assertEqual(len(lines), 6)  # 6 months horizon
        self.assertEqual(
            lines.mapped("forecast_hours"),
            # number of days in the first 6 months of 2022, minus easter in April
            [21.0 * 8, 20.0 * 8, 23.0 * 8, (21.0 - 1) * 8, 22.0 * 8, 22.0 * 8],
        )
        res_ids = self.dev_employee_forecast_role.ids
        self.dev_employee_forecast_role.unlink()
        to_remove_lines = self.ForecastLine.search(
            [("res_id", "in", res_ids), ("res_model", "=", "hr.employee.forecast.role")]
        )
        self.assertFalse(to_remove_lines.exists())

    @freeze_time("2022-01-01 12:00:00")
    def test_calendar_leave_unlink_updates_forecast_lines(self):
        calendar = self.employee_dev.resource_calendar_id

        lines_before = self.ForecastLine.search(
            [
                ("employee_id", "=", self.employee_dev.id),
                ("forecast_role_id", "=", self.role_developer.id),
                ("res_model", "=", self.role_model),
                ("date_from", "=", "2022-04-01"),
            ]
        )
        self.assertEqual(len(lines_before), 1)
        expected_april_hours = 21.0 * 8  # 21 working days × 8 h
        self.assertEqual(lines_before.forecast_hours, expected_april_hours)
        leave = self.env["resource.calendar.leaves"].create(
            {
                "name": "Easter Monday",
                "calendar_id": calendar.id,
                "date_from": "2022-04-18 00:00:00",
                "date_to": "2022-04-19 00:00:00",
                "time_type": "leave",
            }
        )
        self.env.flush_all()

        april_after_create = self.ForecastLine.search(
            [
                ("employee_id", "=", self.employee_dev.id),
                ("forecast_role_id", "=", self.role_developer.id),
                ("res_model", "=", self.role_model),
                ("date_from", "=", "2022-04-01"),
            ]
        )
        self.assertEqual(len(april_after_create), 1)
        self.assertEqual(
            april_after_create.forecast_hours,
            (21.0 - 1) * 8,
            "Creating the leave must reduce the April forecast by 8 h",
        )
        leave.unlink()
        self.env.flush_all()
        april_after_unlink = self.ForecastLine.search(
            [
                ("employee_id", "=", self.employee_dev.id),
                ("forecast_role_id", "=", self.role_developer.id),
                ("res_model", "=", self.role_model),
                ("date_from", "=", "2022-04-01"),
            ]
        )
        self.assertEqual(len(april_after_unlink), 1)
        self.assertEqual(
            april_after_unlink.forecast_hours,
            expected_april_hours,
            "After unlinking the leave, _update_forecast_lines must restore "
            "the April forecast to its original value",
        )

    @freeze_time("2022-01-01 12:00:00")
    def test_calendar_leave_write_updates_forecast_lines(self):
        calendar = self.employee_dev.resource_calendar_id

        def _april_hours():
            line = self.ForecastLine.search(
                [
                    ("employee_id", "=", self.employee_dev.id),
                    ("forecast_role_id", "=", self.role_developer.id),
                    ("res_model", "=", self.role_model),
                    ("date_from", "=", "2022-04-01"),
                ]
            )
            return line.forecast_hours if line else None

        # Baseline: April = 21 working days × 8 h
        april_baseline = 21.0 * 8
        self.assertEqual(_april_hours(), april_baseline)

        # Create a 1-day leave on April 18 → April shrinks by 8 h
        leave = self.env["resource.calendar.leaves"].create(
            {
                "name": "Easter Monday",
                "calendar_id": calendar.id,
                "date_from": "2022-04-18 00:00:00",
                "date_to": "2022-04-19 00:00:00",
                "time_type": "leave",
            }
        )
        self.env.flush_all()
        self.assertEqual(
            _april_hours(),
            (21.0 - 1) * 8,
            "Creating the leave must reduce April by 8 h",
        )

        # Write: extend the leave to 2 days (April 18–20) → April shrinks by another 8 h
        leave.write({"date_to": "2022-04-20 00:00:00"})
        self.env.flush_all()

        self.assertEqual(
            _april_hours(),
            (21.0 - 2) * 8,
            "After extending the leave via write(), April must lose another 8 h",
        )

    @freeze_time("2022-01-01 12:00:00")
    def test_calendar_leave_unlink_global_leave_updates_all_employee_roles(self):
        """When a global leave (no resource_id) is unlinked, _get_resource_roles()
        falls into the else-branch and fetches all employees of the company.
        After unlink, all affected employee forecast lines must be restored.
        """
        # ── Create a global company-wide leave on a March working day ──
        leave = self.env["resource.calendar.leaves"].create(
            {
                "name": "Global Company Holiday",
                "date_from": "2022-03-14 00:00:00",
                "date_to": "2022-03-15 00:00:00",
                "time_type": "leave",
                "company_id": self.env.company.id,
            }
        )
        self.env.flush_all()

        def _march_hours(employee_id, role_id):
            line = self.ForecastLine.search(
                [
                    ("employee_id", "=", employee_id),
                    ("forecast_role_id", "=", role_id),
                    ("res_model", "=", self.role_model),
                    ("date_from", "=", "2022-03-01"),
                ]
            )
            return line.forecast_hours if line else None

        # March 2022 has 23 working days; the global leave removes one → 22 × 8
        self.assertEqual(
            _march_hours(self.employee_dev.id, self.role_developer.id),
            22.0 * 8,
            "Dev: global leave must reduce March forecast by 8 h",
        )
        self.assertEqual(
            _march_hours(self.employee_consultant.id, self.role_consultant.id),
            22.0 * 8,
            "Consultant: global leave must reduce March forecast by 8 h",
        )

        # ── Unlink the global leave ───
        leave.unlink()
        self.env.flush_all()

        # ── Both employees' March lines must be restored to 23 × 8 ───
        self.assertEqual(
            _march_hours(self.employee_dev.id, self.role_developer.id),
            23.0 * 8,
            "Dev March hours must be restored after global leave is deleted",
        )
        self.assertEqual(
            _march_hours(self.employee_consultant.id, self.role_consultant.id),
            23.0 * 8,
            "Consultant March hours must be restored after global leave is deleted",
        )

    @freeze_time("2022-01-01 12:00:00")
    def test_calendar_leave_update_on_empty_recordset(self):
        # Capture baseline March hours
        def _march_hours():
            line = self.ForecastLine.search(
                [
                    ("employee_id", "=", self.employee_dev.id),
                    ("forecast_role_id", "=", self.role_developer.id),
                    ("res_model", "=", self.role_model),
                    ("date_from", "=", "2022-03-01"),
                ]
            )
            return line.forecast_hours if line else None

        march_baseline = 23.0 * 8
        self.assertEqual(_march_hours(), march_baseline)

        # Create a leave to disturb March, then delete it
        calendar = self.employee_dev.resource_calendar_id
        leave = self.env["resource.calendar.leaves"].create(
            {
                "name": "Temp Leave",
                "calendar_id": calendar.id,
                "date_from": "2022-03-14 00:00:00",
                "date_to": "2022-03-15 00:00:00",
                "time_type": "leave",
            }
        )
        self.env.flush_all()
        self.assertEqual(_march_hours(), (23.0 - 1) * 8)

        # Delete the leave so we have an empty recordset
        leave.unlink()
        self.env.flush_all()
        self.assertEqual(_march_hours(), march_baseline)

        # Now call _update_forecast_lines on an empty recordset directly
        # This hits L42: date_start = date_to = None
        empty = self.env["resource.calendar.leaves"].browse()
        empty._update_forecast_lines()
        self.env.flush_all()

        # Hours must remain unchanged (no crash, no side-effect)
        self.assertEqual(
            _march_hours(),
            march_baseline,
            "Calling _update_forecast_lines on an empty recordset "
            "must not crash or alter existing forecast lines",
        )


class TestForecastRoleTimesheet(BaseForecastRoleTest):
    def test_timesheet_forecast_lines(self):
        self.env = self.env(user=self.user_root.id)
        with freeze_time("2022-01-01"):
            with Form(self.env["sale.order"]) as form:
                form.partner_id = self.customer
                form.default_forecast_date_start = "2022-02-14"
                form.default_forecast_date_end = "2022-04-17"
                with form.order_line.new() as line:
                    line.product_id = self.product_dev_tm
                    line.product_uom_qty = (
                        45 * 2
                    )  # 45 working days in the period, sell 2 FTE
                    line.product_uom = self.env.ref("uom.product_uom_day")
            so = form.save()
            so.action_confirm()

        with freeze_time("2022-02-14"):
            line = so.order_line[0]
            task = self.env["project.task"].search([("sale_line_id", "=", line.id)])
            # timesheet 1d
            self.env["account.analytic.line"].create(
                {
                    "employee_id": self.employee_dev.id,
                    "task_id": task.id,
                    "project_id": task.project_id.id,
                    "unit_amount": 8,
                }
            )
            self.env.flush_all()
            if hasattr(task, "_update_forecast_lines"):
                task._update_forecast_lines()
            self.env.invalidate_all()
            forecast_lines = self.ForecastLine.search(
                [("res_id", "=", task.id), ("res_model", "=", "project.task")]
            )
            self.assertEqual(len(forecast_lines), 3)
            daily_ratio = (45 * 2 - 1) * 8 / 45
            self.assertAlmostEqual(
                forecast_lines[0].forecast_hours, -1 * daily_ratio * 11, places=2
            )
            self.assertAlmostEqual(
                forecast_lines[1].forecast_hours, -1 * daily_ratio * 23, places=2
            )
            self.assertAlmostEqual(
                forecast_lines[2].forecast_hours, -1 * daily_ratio * 11, places=2
            )
            self.assertEqual(
                forecast_lines.mapped("date_from"),
                [date(2022, 2, 1), date(2022, 3, 1), date(2022, 4, 1)],
            )
            self.assertEqual(
                forecast_lines.mapped("date_to"),
                [date(2022, 2, 28), date(2022, 3, 31), date(2022, 4, 30)],
            )

    def test_timesheet_forecast_lines_cron(self):
        """check recomputation of forecast lines of tasks even if we don"t TS"""
        self.test_timesheet_forecast_lines()
        with freeze_time("2022-03-10"):
            self.ForecastLine._cron_recompute_all()
            forecast_lines = self.ForecastLine.search(
                [("res_model", "=", "project.task")]
            )
            self.assertEqual(len(forecast_lines), 2)
            daily_ratio = (
                8
                * (45 * 2 - 1)
                / 27  # 27 worked days between 2022-03-10 and 2022-04-17
            )
            self.assertAlmostEqual(
                forecast_lines[0].forecast_hours,
                -1
                * daily_ratio
                * 16,  # 16 worked days between 2022-03-10 and 2022-03-31
            )
            self.assertAlmostEqual(
                forecast_lines[1].forecast_hours,
                -1
                * daily_ratio
                * 11,  # 11 worked days between 2022-04-01 and 2022-04-17
            )
            self.assertEqual(
                forecast_lines.mapped("date_from"),
                [date(2022, 3, 1), date(2022, 4, 1)],
            )
            self.assertEqual(
                forecast_lines.mapped("date_to"),
                [date(2022, 3, 31), date(2022, 4, 30)],
            )


class TestForecastRoleProjectReschedule(BaseForecastRoleTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # for this test, we use a daily granularity
        cls.env.company.write(
            {
                "forecast_line_granularity": "day",
                "forecast_line_horizon": 2,  # months
            }
        )
        ProjectProject = cls.env["project.project"]
        ProjectTask = cls.env["project.task"]
        project = ProjectProject.create({"name": "TestProjectReschedule"})
        # set project in stage "in progress" to get confirmed forecast
        project.stage_id = cls.env.ref("project.project_project_stage_1")
        with freeze_time("2022-02-01 12:00:00"):
            cls.task = ProjectTask.create(
                {
                    "name": "TaskReschedule",
                    "project_id": project.id,
                    "forecast_role_id": cls.role_consultant.id,
                    "forecast_date_planned_start": "2022-02-14",
                    "forecast_date_planned_end": "2022-02-15",
                    "allocated_hours": 16,
                }
            )
            # flush needed here to trigger the recomputation with the correct
            # frozen time (otherwise it is called by the test runner before the
            # tests, outside of the context manager.
            cls.env.flush_all()

    @freeze_time("2022-02-01 12:00:00")
    def test_task_unlink(self):
        task_forecast = self.ForecastLine.search([("task_id", "=", self.task.id)])
        self.task.unlink()
        self.assertFalse(task_forecast.exists())

    @freeze_time("2022-02-01 12:00:00")
    def test_task_forecast_line_reschedule_employee(self):
        """changing the employee will create new lines"""
        self.task.user_ids = self.user_consultant
        if hasattr(self.task, "_update_forecast_lines"):
            self.task._update_forecast_lines()
        task_forecast = self.ForecastLine.search([("task_id", "=", self.task.id)])
        self.assertEqual(task_forecast.mapped("employee_id"), self.employee_consultant)
        self.task.user_ids = self.user_pm
        self.env.flush_all()
        if hasattr(self.task, "_update_forecast_lines"):
            self.task._update_forecast_lines()
        task_forecast_after = self.ForecastLine.search([("task_id", "=", self.task.id)])
        self.assertNotEqual(task_forecast.ids, task_forecast_after.ids)
        self.assertEqual(task_forecast_after.mapped("employee_id"), self.employee_pm)

    @freeze_time("2022-02-01 12:00:00")
    def test_task_forecast_line_reschedule_dates(self):
        """changing the dates will keep the lines which did not change dates"""
        self.task._update_forecast_lines()
        self.env.flush_all()
        task_forecast = self.ForecastLine.search([("task_id", "=", self.task.id)])
        self.assertEqual(task_forecast[0].date_from.strftime("%Y-%m-%d"), "2022-02-14")
        self.task.write(
            {
                "forecast_date_planned_start": "2022-02-15",
                "forecast_date_planned_end": "2022-02-16",
            }
        )
        self.env.flush_all()
        if hasattr(self.task, "_update_forecast_lines"):
            self.task._update_forecast_lines()
        task_forecast_after = self.ForecastLine.search([("task_id", "=", self.task.id)])
        self.assertEqual(
            task_forecast_after[0].date_from.strftime("%Y-%m-%d"), "2022-02-15"
        )
        self.assertEqual(
            task_forecast_after[1].date_from.strftime("%Y-%m-%d"), "2022-02-16"
        )
        self.assertEqual(task_forecast.ids[1], task_forecast_after.ids[0])
        self.assertNotEqual(task_forecast.ids[0], task_forecast_after.ids[1])

    @freeze_time("2022-02-01 12:00:00")
    def test_task_forecast_line_reschedule_time(self):
        """changing the remaining time will keep the forecast lines"""
        self.task.user_ids = self.user_consultant
        self.task._update_forecast_lines()
        self.env.flush_all()
        task_forecast = self.ForecastLine.search([("task_id", "=", self.task.id)])
        self.env["project.task"]._recompute_forecast_lines()
        self.assertEqual(task_forecast.mapped("forecast_hours"), [-8.0, -8.0])
        self.task.write({"allocated_hours": 24})
        self.env.flush_all()
        self.env.invalidate_all()
        task_forecast_after = self.ForecastLine.search(
            [("task_id", "=", self.task.id)], order="id"
        )
        self.assertEqual(task_forecast_after.mapped("forecast_hours"), [-12.0, -12.0])
        self.assertEqual(task_forecast.ids, task_forecast_after.ids)

    @freeze_time("2022-02-01 12:00:00")
    def test_task_forecast_line_reschedule_time_no_employee(self):
        """changing the remaining time will keep the forecast lines, even when no
        employee assigned"""
        self.task._update_forecast_lines()
        self.env.flush_all()
        task_forecast = self.ForecastLine.search([("task_id", "=", self.task.id)])
        self.assertEqual(task_forecast.mapped("forecast_hours"), [-8.0, -8.0])
        self.task.write({"allocated_hours": 24})
        self.task._update_forecast_lines()
        self.env.flush_all()
        task_forecast_after = self.ForecastLine.search([("task_id", "=", self.task.id)])
        self.assertEqual(task_forecast_after.mapped("forecast_hours"), [-12.0, -12.0])
        self.assertEqual(task_forecast.ids, task_forecast_after.ids)


class TestForecastRoleProject(BaseForecastRoleTest):
    @classmethod
    @freeze_time("2022-01-01")
    def setUpClass(cls):
        super().setUpClass()
        # for this test, we use a daily granularity
        cls.env.company.write(
            {
                "forecast_line_granularity": "day",
                "forecast_line_horizon": 2,  # months
            }
        )

    def _get_employee_forecast(self):
        employee_forecast = self.ForecastLine.search(
            [("employee_id", "=", self.employee_consultant.id)]
        )
        # we can take first line to check as forecast values are equal
        forecast_consultant = employee_forecast.filtered(
            lambda x: x.res_model == self.role_model
            and x.forecast_role_id == self.role_consultant
        )[0]
        forecast_pm = employee_forecast.filtered(
            lambda x: x.res_model == self.role_model
            and x.forecast_role_id == self.role_pm
        )[0]
        return forecast_consultant, forecast_pm

    @freeze_time("2022-02-14 12:00:00")
    def test_task_forecast_lines_consolidated_forecast(self):
        # set the consultant employee to 75% consultant and 25% PM
        self.HrEmployeeForecastRole.create(
            {
                "employee_id": self.employee_consultant.id,
                "role_id": self.role_pm.id,
                "date_start": "2022-01-01",
                "rate": 25,
                "sequence": 1,
            }
        )
        consultant_role = self.HrEmployeeForecastRole.search(
            [
                ("employee_id", "=", self.employee_consultant.id),
                ("role_id", "=", self.role_consultant.id),
            ]
        )
        consultant_role.rate = 75
        self.HrEmployeeForecastRole._update_forecast_lines()
        ProjectProject = self.env["project.project"]
        ProjectTask = self.env["project.task"]
        # Create 2 project and 2 tasks with role consultant with 8h planned on
        # 1 day, assigned to the consultant
        #
        # Projet 1 is in TODO (not confirmed forecast)
        project_1 = ProjectProject.create({"name": "TestProject1"})
        # set project in stage "to do" to get forecast
        project_1.stage_id = self.env.ref("project.project_project_stage_0")
        self.env.flush_all()
        task_values = {
            "project_id": project_1.id,
            "forecast_role_id": self.role_consultant.id,
            "forecast_date_planned_start": "2022-02-14",
            "forecast_date_planned_end": "2022-02-14",
            "allocated_hours": 8,
        }
        task_values.update({"name": "Task1"})
        task_1 = ProjectTask.create(task_values)
        task_1.user_ids = self.user_consultant
        task_1._update_forecast_lines()
        task_values.update({"name": "Task2"})
        task_2 = ProjectTask.create(task_values)
        task_2.user_ids = self.user_consultant
        task_2._update_forecast_lines()

        # Project 2 is in stage "in rogress" to get forecast
        project_2 = ProjectProject.create({"name": "TestProject2"})
        project_2.stage_id = self.env.ref("project.project_project_stage_1")
        self.env.flush_all()
        task_values.update({"project_id": project_2.id, "name": "Task3"})
        task_3 = ProjectTask.create(task_values)
        task_3.user_ids = self.user_consultant
        task_3._update_forecast_lines()
        task_values.update({"name": "Task4"})
        task_4 = ProjectTask.create(task_values)
        task_4.user_ids = self.user_consultant
        task_4._update_forecast_lines()
        self.env.flush_all()

        # check forecast lines
        forecast = self.ForecastLine.search(
            [("task_id", "in", (task_1.id, task_2.id, task_3.id, task_4.id))]
        )
        self.assertEqual(len(forecast), 4)
        self.assertEqual(
            forecast.mapped("forecast_hours"),
            [
                -8.0,
            ]
            * 4,
        )
        # consolidated forecast is in days of 8 hours
        self.assertEqual(forecast.mapped("consolidated_forecast"), [1.0] * 4)
        self.assertEqual(
            forecast.filtered(lambda r: r.type == "forecast").mapped(
                "confirmed_consolidated_forecast"
            ),
            [0.0] * 2,
        )
        self.assertEqual(
            forecast.filtered(lambda r: r.type == "confirmed").mapped(
                "confirmed_consolidated_forecast"
            ),
            [1.0] * 2,
        )
        forecast_consultant, forecast_pm = self._get_employee_forecast()
        (forecast_consultant | forecast_pm)._compute_consolidated_forecast()
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertEqual(forecast_consultant.forecast_hours, 6.0)
        # Capacity (6.0h) - Total Consumption (4 * -8.0h = -32.0h) = -26.0h. -26.0 / 8.0 = -3.25 days #noqa: E501
        self.assertAlmostEqual(
            forecast_consultant.consolidated_forecast, -3.25, places=2
        )  # noqa: E501
        # Capacity (6.0h) - Confirmed Consumption (2 * -8.0h = -16.0h) = -10.0h. -10.0 / 8.0 = -1.25 days #noqa: E501
        self.assertAlmostEqual(
            forecast_consultant.confirmed_consolidated_forecast, -1.25, places=2
        )  # noqa: E501
        self.assertAlmostEqual(forecast_pm.forecast_hours, 2.0)
        self.assertAlmostEqual(forecast_pm.consolidated_forecast, 0.25, places=2)  # noqa: E501
        self.assertAlmostEqual(
            forecast_pm.confirmed_consolidated_forecast, 0.25, places=2
        )  # noqa: E501
        res_ids = (project_1 | project_2).task_ids.ids  # noqa: E501
        (project_1 | project_2).task_ids.unlink()  # noqa: E501
        to_remove_lines = self.ForecastLine.search(
            [("res_id", "in", res_ids), ("res_model", "=", "project.task")]
        )  # noqa: E501
        self.assertFalse(to_remove_lines.exists())

    @freeze_time("2022-01-01 12:00:00")
    def test_forecast_with_holidays(self):
        self.test_task_forecast_lines_consolidated_forecast()
        with Form(self.env["hr.leave"]) as form:
            form.employee_id = self.employee_consultant
            form.holiday_status_id = self.env.ref("hr_holidays.holiday_status_unpaid")
            form.request_date_from = "2022-02-14"
            form.request_date_to = "2022-02-15"
        leave_request = form.save()
        # validating the leave request will recompute the forecast lines for
        # the employee capactities (actually delete the existing ones and
        # create new ones -> we check that the project task lines are
        # automatically related to the new newly created employee role lines.
        leave_request.action_validate()
        self.env.flush_all()
        self.env.invalidate_all()
        forecast_lines = self.ForecastLine.search(
            [
                ("employee_id", "=", self.employee_consultant.id),
                ("res_model", "=", self.role_model),
                ("date_from", ">=", "2022-02-14"),
                ("date_to", "<=", "2022-02-15"),
            ]
        )
        # 1 line per role per day -> 4 lines
        self.assertEqual(len(forecast_lines), 2 * 2)
        forecast_lines_consultant = forecast_lines.filtered(
            lambda r: r.forecast_role_id == self.role_consultant
        )
        # both new lines have now a capacity of 0 (employee is on holidays)
        self.assertEqual(forecast_lines_consultant[0].forecast_hours, 0)
        self.assertEqual(forecast_lines_consultant[1].forecast_hours, 0)
        # first line has a negative consolidated forecast (because of the task)
        self.assertEqual(forecast_lines_consultant[0].consolidated_forecast, 0)
        self.assertEqual(forecast_lines_consultant[1].consolidated_forecast, -0)

    def test_task_forecast_lines_consolidated_forecast_overallocation(self):
        ProjectProject = self.env["project.project"]
        ProjectTask = self.env["project.task"]
        with freeze_time("2022-01-01"):
            employee_forecast = self.ForecastLine.search(
                [
                    ("employee_id", "=", self.employee_consultant.id),
                    ("date_from", "=", "2022-02-14"),
                ]
            )
            self.assertEqual(len(employee_forecast), 1)
            project = ProjectProject.create({"name": "TestProject"})
            # set project in stage "in progress" to get confirmed forecast
            project.stage_id = self.env.ref("project.project_project_stage_1")
            self.env.flush_all()
            task = ProjectTask.create(
                {
                    "name": "Task1",
                    "project_id": project.id,
                    "forecast_role_id": self.role_consultant.id,
                    "forecast_date_planned_start": "2022-02-14",
                    "forecast_date_planned_end": "2022-02-14",
                    "allocated_hours": 10,
                }
            )
            task.remaining_hours = 10
            task.user_ids = self.user_consultant
            task._update_forecast_lines()
            self.env.flush_all()
            self.env.invalidate_all()
            forecast = self.ForecastLine.search([("task_id", "=", task.id)])
            self.assertEqual(len(forecast), 1)
            # using assertEqual on purpose here
            self.assertEqual(forecast.forecast_hours, -10.0)
            self.assertEqual(forecast.consolidated_forecast, 1.25)
            self.assertEqual(forecast.confirmed_consolidated_forecast, 1.25)
            self.assertEqual(
                forecast.employee_resource_forecast_line_id.consolidated_forecast,
                -0.25,
            )
            self.assertEqual(
                forecast.employee_resource_forecast_line_id.confirmed_consolidated_forecast,
                -0.25,
            )

    def test_task_forecast_lines_consolidated_forecast_overallocation_multiple_tasks(
        self,
    ):
        ProjectProject = self.env["project.project"]
        ProjectTask = self.env["project.task"]
        with freeze_time("2022-01-01"):
            employee_forecast = self.ForecastLine.search(
                [
                    ("employee_id", "=", self.employee_consultant.id),
                    ("date_from", "=", "2022-02-14"),
                ]
            )
            self.assertEqual(len(employee_forecast), 1)
            project = ProjectProject.create({"name": "TestProject"})
            # set project in stage "in progress" to get confirmed forecast
            project.stage_id = self.env.ref("project.project_project_stage_1")
            self.env.flush_all()
            task1 = ProjectTask.create(
                {
                    "name": "Task1",
                    "project_id": project.id,
                    "forecast_role_id": self.role_consultant.id,
                    "forecast_date_planned_start": "2022-02-14",
                    "forecast_date_planned_end": "2022-02-14",
                    "allocated_hours": 8,
                }
            )
            task1.remaining_hours = 10
            task1.user_ids = self.user_consultant
            task1._update_forecast_lines()
            self.env.flush_all()
            forecast1 = self.ForecastLine.search([("task_id", "=", task1.id)])
            self.assertEqual(len(forecast1), 1)
            task2 = ProjectTask.create(
                {
                    "name": "Task2",
                    "project_id": project.id,
                    "forecast_role_id": self.role_consultant.id,
                    "forecast_date_planned_start": "2022-02-14",
                    "forecast_date_planned_end": "2022-02-14",
                    "allocated_hours": 4,
                }
            )
            task2.remaining_hours = 4
            task2.user_ids = self.user_consultant
            task2._update_forecast_lines()
            self.env.flush_all()
            forecast2 = self.ForecastLine.search([("task_id", "=", task2.id)])
            # using assertEqual on purpose here
            self.assertEqual(
                forecast1.employee_resource_forecast_line_id,
                forecast2.employee_resource_forecast_line_id,
            )
            self.assertAlmostEqual(
                forecast1.employee_resource_forecast_line_id.consolidated_forecast,
                -0.75,
                places=2,
            )
            self.assertAlmostEqual(
                forecast1.employee_resource_forecast_line_id.confirmed_consolidated_forecast,
                -0.75,
                places=2,
            )

    @freeze_time("2022-01-03 12:00:00")
    def test_task_forecast_lines_employee_different_roles(self):
        """
        Test forecast lines when employee has different roles.

        Employee has 2 forecast_role_id: consultant 75% and project manager 25%,
        working 8h per day (standard calendar).
        Create a task with forecast role consultant, with remaining time = 8h
        and a scheduled period starting and ending on the same day (today for instance).
        Assign this task to the user.

        Expected: for the user, on today, 3 forecast lines.

        res_model	                forecast_role_id  forecast_hours consolidated_forecast
        project.task	            consultant	         -8	             1 (in days)
        hr.employee.forecast.role	consultant	          6	            -0.25 (in days)
        hr.employee.forecast.role	project manager	      2	             0.25 (in days)

        """  # noqa: E501
        ProjectProject = self.env["project.project"]
        ProjectTask = self.env["project.task"]
        self.HrEmployeeForecastRole.create(
            {
                "employee_id": self.employee_consultant.id,
                "role_id": self.role_pm.id,
                "date_start": "2022-01-01",
                "rate": 25,
                "sequence": 1,
            }
        )
        consultant_role = self.HrEmployeeForecastRole.search(
            [
                ("employee_id", "=", self.employee_consultant.id),
                ("role_id", "=", self.role_consultant.id),
            ]
        )
        consultant_role.rate = 75
        project = ProjectProject.create({"name": "TestProjectDiffRoles"})
        # set project in stage "in progress" to get confirmed forecast
        project.stage_id = self.env.ref("project.project_project_stage_1")
        self.env.flush_all()
        task = ProjectTask.create(
            {
                "name": "TaskDiffRoles",
                "project_id": project.id,
                "forecast_role_id": self.role_consultant.id,
                "forecast_date_planned_start": date.today(),
                "forecast_date_planned_end": date.today(),
                "allocated_hours": 8,
            }
        )
        task.user_ids = self.user_consultant
        task._update_forecast_lines()
        self.env.flush_all()
        self.env.invalidate_all()
        task_forecast = self.ForecastLine.search([("task_id", "=", task.id)])
        self.assertEqual(len(task_forecast), 1)
        # using assertEqual on purpose here
        self.assertEqual(task_forecast.forecast_hours, -8.0)
        self.assertEqual(task_forecast.consolidated_forecast, 1.0)
        self.assertEqual(task_forecast.confirmed_consolidated_forecast, 1.0)
        forecast_consultant, forecast_pm = self._get_employee_forecast()
        self.assertEqual(forecast_consultant.forecast_hours, 6.0)
        self.assertAlmostEqual(
            forecast_consultant.consolidated_forecast, -0.25, places=2
        )
        self.assertAlmostEqual(
            forecast_consultant.confirmed_consolidated_forecast, -0.25, places=2
        )  # noqa: E501
        self.assertEqual(forecast_pm.forecast_hours, 2.0)
        self.assertAlmostEqual(forecast_pm.consolidated_forecast, 0.25, places=2)
        self.assertAlmostEqual(
            forecast_pm.confirmed_consolidated_forecast, 0.25, places=2
        )

    @freeze_time("2022-01-03 12:00:00")  # noqa: E501
    def test_task_forecast_lines_employee_main_role(self):
        """
        Test forecast lines when employee has different roles
        and different from employee's role is assigned to the task.

        Employee has 2 forecast_role_id: consultant 75% and project manager 25%,
        working 8h per day (standard calendar).
        Create a task with forecast role developer, with remaining time = 8h
        and a scheduled period starting and ending on the same day (today for instance).
        Assign this task to the user.

        Expected: for the user, on today, 3 forecast lines.

        res_model	                forecast_role_id  forecast_hours consolidated_forecast
        project.task	            consultant	         -8	             1 (in days)
        hr.employee.forecast.role	consultant	          6	            -0.25 (in days)
        hr.employee.forecast.role	project manager	      2	             0.25 (in days)

        """  # noqa: E501
        ProjectProject = self.env["project.project"]
        ProjectTask = self.env["project.task"]
        self.HrEmployeeForecastRole.create(
            {
                "employee_id": self.employee_consultant.id,
                "role_id": self.role_pm.id,
                "date_start": "2022-01-01",
                "rate": 25,
                "sequence": 1,
            }
        )
        consultant_role = self.HrEmployeeForecastRole.search(
            [
                ("employee_id", "=", self.employee_consultant.id),
                ("role_id", "=", self.role_consultant.id),
            ]
        )
        consultant_role.rate = 75
        project = ProjectProject.create({"name": "TestProjectDiffRoles"})
        # set project in stage "in progress" to get confirmed forecast
        project.stage_id = self.env.ref("project.project_project_stage_1")
        self.env.flush_all()
        task = ProjectTask.create(
            {
                "name": "TaskDiffRoles",
                "project_id": project.id,
                "forecast_role_id": self.role_developer.id,
                "forecast_date_planned_start": date(2022, 1, 1),
                "forecast_date_planned_end": date(2022, 1, 1),
                "allocated_hours": 8,
            }
        )
        self.env.flush_all()
        task.user_ids = self.user_consultant
        task._update_forecast_lines()
        task_forecast = self.ForecastLine.search([("task_id", "=", task.id)])
        self.assertEqual(len(task_forecast), 1)
        # using assertEqual on purpose here
        self.assertEqual(task_forecast.forecast_hours, -8.0)
        self.assertEqual(task_forecast.consolidated_forecast, 1.0)
        self.assertEqual(task_forecast.confirmed_consolidated_forecast, 1.0)
        forecast_consultant, forecast_pm = self._get_employee_forecast()
        self.assertEqual(forecast_consultant.forecast_hours, 6.0)
        self.assertAlmostEqual(forecast_consultant.consolidated_forecast, -0.25)
        self.assertAlmostEqual(
            forecast_consultant.confirmed_consolidated_forecast, -0.25
        )
        self.assertEqual(forecast_pm.forecast_hours, 2.0)
        self.assertAlmostEqual(forecast_pm.consolidated_forecast, 0.25)
        self.assertAlmostEqual(forecast_pm.confirmed_consolidated_forecast, 0.25)


@tagged("-at_install", "post_install")
@freeze_time("2022-01-01")
class TestForecastRoleCoverage(BaseForecastRoleTest):
    def test_write_redundant(self):
        employee = self.employee_dev
        line = self.ForecastLine.create(
            {
                "name": "Pruning Test",
                "employee_id": employee.id,
                "forecast_role_id": self.role_developer.id,
                "res_model": "test",
                "date_from": date(2022, 2, 1),
                "date_to": date(2022, 2, 28),
                "type": "forecast",
            }
        )
        # Pruning redundant values
        res = line.write(
            {
                "date_from": line.date_from,
                "type": line.type,
                "res_model": line.res_model,
                "employee_id": line.employee_id.id,
            }
        )
        self.assertTrue(res)

    def test_uom_conversions(self):
        """Lines 443-445: Test convert_days_to_hours"""
        hours = self.ForecastLine.convert_days_to_hours(1)
        self.assertEqual(hours, 8.0)

    @freeze_time("2022-02-14")
    def test_compute_employee_forecast_line_id_fallback(self):
        """Lines 153-162: Fallback to main role"""
        employee = self.employee_dev
        employee.main_role_id = self.role_developer

        # Confirmed line for MAIN role (developer)
        main_role_line = self.ForecastLine.create(
            {
                "name": "Main Role Line",
                "employee_id": employee.id,
                "forecast_role_id": self.role_developer.id,
                "res_model": "hr.employee.forecast.role",
                "date_from": date(2022, 2, 1),
                "date_to": date(2022, 2, 28),
                "type": "confirmed",
            }
        )

        # Forecast line for DIFFERENT role (consultant)
        test_line = self.ForecastLine.create(
            {
                "name": "Consultant Task",
                "employee_id": employee.id,
                "forecast_role_id": self.role_consultant.id,
                "res_model": "project.task",
                "date_from": date(2022, 2, 1),
                "date_to": date(2022, 2, 28),
                "type": "forecast",
            }
        )
        self.assertEqual(test_line.employee_resource_forecast_line_id, main_role_line)

    def test_get_grouped_line_values_and_consolidation(self):
        """Lines 177-180, 203-209: Non-resource consolidation and grouped values"""
        # Create a non-resource line
        task_line = self.ForecastLine.create(
            {
                "name": "Task Line",
                "forecast_hours": 16,
                "res_model": "project.task",
                "date_from": date(2022, 2, 1),
                "date_to": date(2022, 2, 28),
                "type": "confirmed",
                "forecast_role_id": self.role_developer.id,
            }
        )
        # 16h -> 2 days -> -2.0 (standard 8h/day)
        self.assertEqual(task_line.consolidated_forecast, -2.0)
        self.assertEqual(task_line.confirmed_consolidated_forecast, -2.0)

        # Unconfirmed
        task_line_unconfirmed = self.ForecastLine.create(
            {
                "name": "Task Line Unconfirmed",
                "forecast_hours": 8,
                "res_model": "project.task",
                "date_from": date(2022, 2, 1),
                "date_to": date(2022, 2, 28),
                "type": "forecast",
                "forecast_role_id": self.role_developer.id,
            }
        )
        self.assertEqual(task_line_unconfirmed.consolidated_forecast, -1.0)
        self.assertEqual(task_line_unconfirmed.confirmed_consolidated_forecast, 0.0)

    def test_prepare_forecast_lines_no_employee(self):
        """Lines 307-308: _prepare_forecast_lines without employee"""
        vals = self.ForecastLine._prepare_forecast_lines(
            "Test",
            date(2022, 1, 1),
            date(2022, 1, 31),
            "forecast",
            8,
            100,
            res_model="test",
            forecast_role_id=self.role_developer.id,
        )
        self.assertTrue(len(vals) > 0)

    @freeze_time("2022-01-01")
    def test_split_per_period_zero_forecast_warning(self):
        """Lines 355-367: Resource has 0 forecast on period"""
        empty_calendar = self.env["resource.calendar"].create(
            {"name": "Empty Calendar", "attendance_ids": []}
        )
        employee = self.env["hr.employee"].create(
            {"name": "No Work Employee", "resource_calendar_id": empty_calendar.id}
        )

        vals = self.ForecastLine._prepare_forecast_lines(
            "Test Zero",
            date(2022, 2, 1),
            date(2022, 2, 28),
            "forecast",
            8,
            100,
            employee_id=employee.id,
            res_model="test",
        )
        self.assertEqual(len(vals), 1)
        self.assertEqual(vals[0]["date_from"], date(2022, 3, 1))

    def test_split_per_period_zero_daily_forecast(self):
        """Line 370: daily_forecast == 0"""
        vals = list(
            self.ForecastLine._split_per_period(
                date(2022, 1, 1),
                date(2022, 1, 31),
                0,
                100,
                self.employee_dev.resource_id,
                self.employee_dev.resource_calendar_id,
            )
        )
        self.assertEqual(len(vals), 0)

    def test_cron_recompute_all_options(self):
        """Lines 404, 415: Cron recompute with options"""
        self.ForecastLine._cron_recompute_all(
            force_company_id=self.env.company.id, force_delete=True
        )
        self.ForecastLine._cron_recompute_all()

    def test_forecast_hours(self):
        ProjectTasks_2 = self.ProjectTask.create(
            {
                "name": "test_02",
                "project_id": self.project.id,
            }
        )
        self.ProjectTasks.write({"allocated_hours": 8.0})
        self.forecast_line_one._compute_forecast_hours()
        self.env.flush_all()
        count = self.ForecastLine.search_count([("task_id", "=", self.ProjectTasks.id)])
        self.assertEqual(count, 1, "Should be one as we have only created one record")
        # Testing logics:  forecast_hours = -(allocated_hours / number of forecast_lines) --> -(8/2) #noqa: E501
        self.assertEqual(self.forecast_line_one.forecast_hours, -8.0)

        # =========== Checking condition without allocated_hours =============
        ProjectTasks_2.write({"allocated_hours": 0.0})
        self.forecast_line_other.write(
            {
                "res_id": ProjectTasks_2.id,
                "task_id": ProjectTasks_2.id,
            }
        )
        count = self.ForecastLine.search_count([("task_id", "=", ProjectTasks_2.id)])
        self.assertEqual(count, 1, "Should be one as we have only created one record")
        try:
            self.forecast_line_other._compute_forecast_hours()
        except ZeroDivisionError:
            self.env.flush_all()
            self.assertEqual(self.forecast_line_one.forecast_hours, 0.0)
