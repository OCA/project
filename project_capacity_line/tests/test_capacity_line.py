# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date

from freezegun import freeze_time

from odoo.tests.common import Form, TransactionCase


class BaseCapacityLineTest(TransactionCase):
    @classmethod
    @freeze_time("2022-01-01")
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.write(
            {
                "capacity_line_granularity": "month",
                "capacity_line_horizon": 6,  # months
            }
        )
        cls.role_developer = cls.env["capacity.role"].create({"name": "developer"})
        cls.role_consultant = cls.env["capacity.role"].create({"name": "consultant"})
        cls.role_pm = cls.env["capacity.role"].create({"name": "project manager"})
        cls.employee_dev = cls.env["hr.employee"].create({"name": "John Dev"})
        cls.user_consultant = cls.env["res.users"].create(
            {"name": "John Consultant", "login": "jc@example.com"}
        )
        cls.employee_consultant = cls.env["hr.employee"].create(
            {"name": "John Consultant", "user_id": cls.user_consultant.id}
        )
        cls.employee_pm = cls.env["hr.employee"].create({"name": "John Peem"})
        cls.env["hr.employee.capacity.role"].create(
            {
                "employee_id": cls.employee_dev.id,
                "role_id": cls.role_developer.id,
                "date_start": "2022-01-01",
                "sequence": 1,
            }
        )
        cls.env["hr.employee.capacity.role"].create(
            {
                "employee_id": cls.employee_consultant.id,
                "role_id": cls.role_consultant.id,
                "date_start": "2022-01-01",
                "sequence": 1,
            }
        )
        cls.env["hr.employee.capacity.role"].create(
            {
                "employee_id": cls.employee_pm.id,
                "role_id": cls.role_pm.id,
                "date_start": "2022-01-01",
                "sequence": 1,
            }
        )

        cls.product_dev_tm = cls.env["product.product"].create(
            {
                "name": "development time and material",
                "detailed_type": "service",
                "service_tracking": "task_in_project",
                "price": 95,
                "standard_price": 75,
                "capacity_role_id": cls.role_developer.id,
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
                "uom_po_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )
        cls.product_consultant_tm = cls.env["product.product"].create(
            {
                "name": "consultant time and material",
                "detailed_type": "service",
                "service_tracking": "task_in_project",
                "price": 100,
                "standard_price": 80,
                "capacity_role_id": cls.role_consultant.id,
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
                "uom_po_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )

        cls.product_pm_tm = cls.env["product.product"].create(
            {
                "name": "pm time and material",
                "detailed_type": "service",
                "service_tracking": "task_in_project",
                "price": 120,
                "standard_price": 100,
                "capacity_role_id": cls.role_consultant.id,
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
                "uom_po_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )
        cls.customer = cls.env["res.partner"].create({"name": "Some Customer"})


class TestCapacityLineEmployee(BaseCapacityLineTest):
    def test_employee_main_role(self):
        self.env["hr.employee.capacity.role"].create(
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
    def test_employee_capacity(self):
        lines = self.env["capacity.line"].search(
            [
                ("employee_id", "=", self.employee_consultant.id),
                ("capacity_role_id", "=", self.role_consultant.id),
                ("res_model", "=", "hr.employee.capacity.role"),
            ]
        )
        self.assertEqual(len(lines), 6)  # 6 months horizon
        self.assertEqual(
            lines.mapped("capacity_hours"),
            # number of working days in the first 6 months of 2022, no vacations
            [21.0 * 8, 20.0 * 8, 23.0 * 8, 21.0 * 8, 22.0 * 8, 22.0 * 8],
        )

    @freeze_time("2022-01-01")
    def test_employee_capacity_change_roles(self):
        # employee becomes 50% consultant, 50% PM on Feb 1st
        roles = self.employee_consultant.role_ids
        roles.write({"date_end": "2022-01-31"})
        lines = self.env["capacity.line"].search(
            [
                ("employee_id", "=", self.employee_consultant.id),
                ("capacity_role_id", "=", self.role_consultant.id),
                ("res_model", "=", "hr.employee.capacity.role"),
            ]
        )
        self.assertEqual(len(lines), 1)  # 100% consultant role now ends on 31/01
        self.assertEqual(lines.capacity_hours, 21.0 * 8)
        self.env["hr.employee.capacity.role"].create(
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
        lines = self.env["capacity.line"].search(
            [
                ("employee_id", "=", self.employee_consultant.id),
                ("capacity_role_id", "=", self.role_consultant.id),
            ]
        )
        self.assertEqual(len(lines), 6)  # 6 months horizon
        self.assertEqual(
            lines.mapped("capacity_hours"),
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

    @freeze_time("2022-01-01 12:00:00")
    def test_capacity_with_calendar(self):
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
        lines = self.env["capacity.line"].search(
            [
                ("employee_id", "=", self.employee_dev.id),
                ("capacity_role_id", "=", self.role_developer.id),
                ("res_model", "=", "hr.employee.capacity.role"),
            ]
        )
        self.assertEqual(len(lines), 6)  # 6 months horizon
        self.assertEqual(
            lines.mapped("capacity_hours"),
            # number of days in the first 6 months of 2022, minus easter in April
            [21.0 * 8, 20.0 * 8, 23.0 * 8, (21.0 - 1) * 8, 22.0 * 8, 22.0 * 8],
        )


class TestCapacityLineSales(BaseCapacityLineTest):
    @freeze_time("2022-01-01")
    def test_draft_sale_order_creates_negative_forecast_capacity(self):
        with Form(self.env["sale.order"]) as form:
            form.partner_id = self.customer
            form.date_order = "2022-01-10 08:00:00"
            form.default_capacity_date_start = "2022-02-07"
            form.default_capacity_date_end = "2022-02-20"
            with form.order_line.new() as line:
                line.product_id = self.product_dev_tm
                line.product_uom_qty = 10  # 1 FTE sold
                line.product_uom = self.env.ref("uom.product_uom_day")
        so = form.save()
        line = so.order_line[0]
        self.assertEqual(line.capacity_date_start, date(2022, 2, 7))
        self.assertEqual(line.capacity_date_end, date(2022, 2, 20))
        capacity_lines = self.env["capacity.line"].search(
            [
                ("sale_line_id", "=", line.id),
                ("res_model", "=", "sale.order.line"),
            ]
        )
        self.assertEqual(len(capacity_lines), 1)  # 10 days on 2022-02-01 to 2022-02-10
        self.assertEqual(capacity_lines.type, "forecast")
        self.assertEqual(
            capacity_lines.capacity_role_id,
            self.product_dev_tm.capacity_role_id,
        )
        self.assertEqual(capacity_lines.capacity_hours, -10 * 8)
        self.assertEqual(capacity_lines.cost, -10 * 8 * 75)
        self.assertEqual(capacity_lines.date_from, date(2022, 2, 1))
        self.assertEqual(capacity_lines.date_to, date(2022, 2, 28))

    @freeze_time("2022-01-01")
    def test_draft_sale_order_without_dates_no_capacity(self):
        """a draft sale order with no dates on the line does not create capacity"""
        with Form(self.env["sale.order"]) as form:
            form.partner_id = self.customer
            form.date_order = "2022-01-10 08:00:00"
            form.default_capacity_date_start = "2022-02-07"
            form.default_capacity_date_end = False
            with form.order_line.new() as line:
                line.product_id = self.product_dev_tm
                line.product_uom_qty = 10  # 1 FTE sold
                line.product_uom = self.env.ref("uom.product_uom_day")
        so = form.save()
        line = so.order_line[0]
        self.assertEqual(line.capacity_date_start, date(2022, 2, 7))
        self.assertEqual(line.capacity_date_end, False)
        capacity_lines = self.env["capacity.line"].search(
            [
                ("sale_line_id", "=", line.id),
                ("res_model", "=", "sale.order.line"),
            ]
        )
        self.assertFalse(capacity_lines)

    @freeze_time("2022-01-01")
    def test_draft_sale_order_capacity_spread(self):
        with Form(self.env["sale.order"]) as form:
            form.partner_id = self.customer
            form.date_order = "2022-01-10 08:00:00"
            form.default_capacity_date_start = "2022-02-07"
            form.default_capacity_date_end = "2022-04-17"
            with form.order_line.new() as line:
                line.product_id = self.product_dev_tm
                line.product_uom_qty = 100  # sell 2 FTE
                line.product_uom = self.env.ref("uom.product_uom_day")

        so = form.save()
        line = so.order_line[0]
        self.assertEqual(line.capacity_date_start, date(2022, 2, 7))
        self.assertEqual(line.capacity_date_end, date(2022, 4, 17))
        capacity_lines = self.env["capacity.line"].search(
            [
                ("sale_line_id", "=", line.id),
                ("res_model", "=", "sale.order.line"),
            ]
        )
        self.assertEqual(len(capacity_lines), 3)
        daily_ratio = 2 * 8  # 2 FTE * 8h days
        self.assertAlmostEqual(
            capacity_lines[0].capacity_hours,
            -1 * daily_ratio * 16,  # 16 worked days between 2022 Feb 7 and Feb 28
        )
        self.assertAlmostEqual(
            capacity_lines[1].capacity_hours,
            -1 * daily_ratio * 23,  # 23 worked days in march 2022
        )
        self.assertAlmostEqual(
            capacity_lines[2].capacity_hours,
            -1 * daily_ratio * 11,  # 11 worked day between april 1 and 17 2022
        )
        self.assertEqual(
            capacity_lines.mapped("date_from"),
            [date(2022, 2, 1), date(2022, 3, 1), date(2022, 4, 1)],
        )
        self.assertEqual(
            capacity_lines.mapped("date_to"),
            [date(2022, 2, 28), date(2022, 3, 31), date(2022, 4, 30)],
        )

    @freeze_time("2022-01-01")
    def test_confirm_order_sale_order_no_capacity_line(self):
        with Form(self.env["sale.order"]) as form:
            form.partner_id = self.customer
            form.date_order = "2022-01-10 08:00:00"
            form.default_capacity_date_start = "2022-02-14"
            form.default_capacity_date_end = "2022-04-14"
            with form.order_line.new() as line:
                line.product_id = self.product_dev_tm
                line.product_uom_qty = 60
                line.product_uom = self.env.ref("uom.product_uom_day")

        so = form.save()
        so.action_confirm()
        line = so.order_line[0]
        capacity_lines = self.env["capacity.line"].search(
            [
                ("sale_line_id", "=", line.id),
                ("res_model", "=", "sale.order.line"),
            ]
        )
        self.assertFalse(capacity_lines)

    @freeze_time("2022-01-01")
    def test_confirm_order_sale_order_create_project_task_with_capacity_line(self):
        with Form(self.env["sale.order"]) as form:
            form.partner_id = self.customer
            form.date_order = "2022-01-10 08:00:00"
            form.default_capacity_date_start = "2022-02-14"
            form.default_capacity_date_end = "2022-04-17"
            with form.order_line.new() as line:
                line.product_id = self.product_dev_tm
                line.product_uom_qty = 45 * 2  # 2 FTE
                line.product_uom = self.env.ref("uom.product_uom_day")
        so = form.save()
        so.action_confirm()
        line = so.order_line[0]
        task = self.env["project.task"].search([("sale_line_id", "=", line.id)])
        capacity_lines = self.env["capacity.line"].search(
            [("res_id", "=", task.id), ("res_model", "=", "project.task")]
        )
        self.assertEqual(len(capacity_lines), 3)
        self.assertEqual(capacity_lines.mapped("capacity_role_id"), self.role_developer)
        daily_ratio = 8 * 2  # 2 FTE
        self.assertAlmostEqual(
            capacity_lines[0].capacity_hours,
            -1 * daily_ratio * 11,  # 11 working days on 2022-02-14 -> 2022-02-28
        )
        self.assertAlmostEqual(
            capacity_lines[1].capacity_hours,
            -1 * daily_ratio * 23,  # 23 working days on 2022-03-01 -> 2022-03-31
        )
        self.assertAlmostEqual(
            capacity_lines[2].capacity_hours,
            -1 * daily_ratio * 11,  # 11 working days on 2022-04-01 -> 2022-04-17
        )


class TestCapacityLineTimesheet(BaseCapacityLineTest):
    def test_timesheet_capacity_lines(self):
        with freeze_time("2022-01-01"):
            with Form(self.env["sale.order"]) as form:
                form.partner_id = self.customer
                form.date_order = "2022-01-10 08:00:00"
                form.default_capacity_date_start = "2022-02-14"
                form.default_capacity_date_end = "2022-04-17"
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
            capacity_lines = self.env["capacity.line"].search(
                [("res_id", "=", task.id), ("res_model", "=", "project.task")]
            )
            self.assertEqual(len(capacity_lines), 3)
            daily_ratio = (45 * 2 - 1) * 8 / 45
            self.assertAlmostEqual(
                capacity_lines[0].capacity_hours, -1 * daily_ratio * 11
            )
            self.assertAlmostEqual(
                capacity_lines[1].capacity_hours, -1 * daily_ratio * 23
            )
            self.assertAlmostEqual(
                capacity_lines[2].capacity_hours, -1 * daily_ratio * 11
            )
            self.assertEqual(
                capacity_lines.mapped("date_from"),
                [date(2022, 2, 1), date(2022, 3, 1), date(2022, 4, 1)],
            )
            self.assertEqual(
                capacity_lines.mapped("date_to"),
                [date(2022, 2, 28), date(2022, 3, 31), date(2022, 4, 30)],
            )

    def test_timesheet_capacity_lines_cron(self):
        """check recomputation of capacity lines of tasks even if we don't TS"""
        self.test_timesheet_capacity_lines()
        with freeze_time("2022-03-10"):
            self.env["capacity.line"]._cron_recompute_all()
            capacity_lines = self.env["capacity.line"].search(
                [("res_model", "=", "project.task")]
            )
            self.assertEqual(len(capacity_lines), 2)
            daily_ratio = (
                8
                * (45 * 2 - 1)
                / 27  # 27 worked days between 2022-03-10 and 2022-04-17
            )
            self.assertAlmostEqual(
                capacity_lines[0].capacity_hours,
                -1
                * daily_ratio
                * 16,  # 16 worked days between 2022-03-10 and 2022-03-31
            )
            self.assertAlmostEqual(
                capacity_lines[1].capacity_hours,
                -1
                * daily_ratio
                * 11,  # 11 worked days between 2022-04-01 and 2022-04-17
            )
            self.assertEqual(
                capacity_lines.mapped("date_from"),
                [date(2022, 3, 1), date(2022, 4, 1)],
            )
            self.assertEqual(
                capacity_lines.mapped("date_to"),
                [date(2022, 3, 31), date(2022, 4, 30)],
            )


class TestCapacityLineProject(BaseCapacityLineTest):
    @classmethod
    @freeze_time("2022-01-01")
    def setUpClass(cls):
        super().setUpClass()
        # for this test, we use a daily granularity
        cls.env.company.write(
            {
                "capacity_line_granularity": "day",
                "capacity_line_horizon": 2,  # months
            }
        )

    def test_task_capacity_lines_consolidated_capacity(self):
        with freeze_time("2022-01-01"):
            employee_capacity = self.env["capacity.line"].search(
                [
                    ("employee_id", "=", self.employee_consultant.id),
                    ("date_from", "=", "2022-02-14"),
                ]
            )
            self.assertEqual(len(employee_capacity), 1)
            project = self.env["project.project"].create({"name": "TestProject"})
            # set project in stage "in progress" to get confirmed capacity
            project.stage_id = self.env.ref("project.project_project_stage_1")
            task = self.env["project.task"].create(
                {
                    "name": "Task1",
                    "project_id": project.id,
                    "capacity_role_id": self.role_consultant.id,
                    "capacity_date_planned_start": "2022-02-14",
                    "capacity_date_planned_end": "2022-02-14",
                    "planned_hours": 6,
                }
            )
            task.remaining_hours = 6
            task.user_ids = self.user_consultant
            capacity = self.env["capacity.line"].search([("task_id", "=", task.id)])
            self.assertEqual(len(capacity), 1)
            # using assertEqual on purpose here
            self.assertEqual(capacity.capacity_hours, -6.0)
            self.assertEqual(capacity.consolidated_capacity_hours, 6.0)
            self.assertEqual(
                capacity.employee_resource_capacity_line_id.consolidated_capacity_hours,
                2.0,
            )

    def test_task_capacity_lines_consolidated_capacity_overallocation(self):
        with freeze_time("2022-01-01"):
            employee_capacity = self.env["capacity.line"].search(
                [
                    ("employee_id", "=", self.employee_consultant.id),
                    ("date_from", "=", "2022-02-14"),
                ]
            )
            self.assertEqual(len(employee_capacity), 1)
            project = self.env["project.project"].create({"name": "TestProject"})
            # set project in stage "in progress" to get confirmed capacity
            project.stage_id = self.env.ref("project.project_project_stage_1")
            task = self.env["project.task"].create(
                {
                    "name": "Task1",
                    "project_id": project.id,
                    "capacity_role_id": self.role_consultant.id,
                    "capacity_date_planned_start": "2022-02-14",
                    "capacity_date_planned_end": "2022-02-14",
                    "planned_hours": 8,
                }
            )
            task.remaining_hours = 10
            task.user_ids = self.user_consultant
            capacity = self.env["capacity.line"].search([("task_id", "=", task.id)])
            self.assertEqual(len(capacity), 1)
            # using assertEqual on purpose here
            self.assertEqual(capacity.capacity_hours, -10.0)
            self.assertEqual(capacity.consolidated_capacity_hours, 10.0)
            self.assertEqual(
                capacity.employee_resource_capacity_line_id.consolidated_capacity_hours,
                -2.0,
            )

    def test_task_capacity_lines_consolidated_capacity_overallocation_multiple_tasks(
        self,
    ):
        with freeze_time("2022-01-01"):
            employee_capacity = self.env["capacity.line"].search(
                [
                    ("employee_id", "=", self.employee_consultant.id),
                    ("date_from", "=", "2022-02-14"),
                ]
            )
            self.assertEqual(len(employee_capacity), 1)
            project = self.env["project.project"].create({"name": "TestProject"})
            # set project in stage "in progress" to get confirmed capacity
            project.stage_id = self.env.ref("project.project_project_stage_1")
            task1 = self.env["project.task"].create(
                {
                    "name": "Task1",
                    "project_id": project.id,
                    "capacity_role_id": self.role_consultant.id,
                    "capacity_date_planned_start": "2022-02-14",
                    "capacity_date_planned_end": "2022-02-14",
                    "planned_hours": 8,
                }
            )
            task1.remaining_hours = 10
            task1.user_ids = self.user_consultant
            capacity1 = self.env["capacity.line"].search([("task_id", "=", task1.id)])
            self.assertEqual(len(capacity1), 1)
            task2 = self.env["project.task"].create(
                {
                    "name": "Task2",
                    "project_id": project.id,
                    "capacity_role_id": self.role_consultant.id,
                    "capacity_date_planned_start": "2022-02-14",
                    "capacity_date_planned_end": "2022-02-14",
                    "planned_hours": 4,
                }
            )
            task2.remaining_hours = 4
            task2.user_ids = self.user_consultant
            capacity2 = self.env["capacity.line"].search([("task_id", "=", task2.id)])
            # using assertEqual on purpose here
            self.assertEqual(
                capacity1.employee_resource_capacity_line_id,
                capacity2.employee_resource_capacity_line_id,
            )
            self.assertEqual(
                capacity1.employee_resource_capacity_line_id.consolidated_capacity_hours,
                -6.0,
            )
