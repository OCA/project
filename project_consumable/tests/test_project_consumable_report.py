# Copyright 2021 - Pierre Verkest
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from odoo.tests import TransactionCase


class TestProjectConsumableReporting(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("project_consumable.product_coffee_capsule")
        default_plan_id = cls.env["account.analytic.plan"].search([], limit=1)
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test",
                "plan_id": default_plan_id.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test",
                "analytic_account_id": cls.analytic_account.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.employee = cls.user_demo.employee_id

        cls.env["hr.attendance"].create(
            {
                "employee_id": cls.employee.id,
                "check_in": datetime(2022, 2, 9, 8, 0),  # Wednesday
                "check_out": datetime(2022, 2, 9, 16, 0),
            }
        )

    def _prepare_consumable_line_data(self, **kwargs):
        data = {
            "name": "collect test material",
            "project_id": self.project.id,
            "account_id": None,
            "product_id": self.product.id,
            "unit_amount": 6,
            "employee_id": self.employee.id,
            "product_uom_id": self.product.uom_id.id,
            "task_id": None,
            "amount": None,
            "date": None,
            "partner_id": None,
        }
        data.update(**kwargs)
        return {k: v for k, v in data.items() if v is not None}

    def test_timesheet_analysis_report_exclude_consumable(self):
        self.env["account.analytic.line"].create(
            {
                "name": "test timesheet",
                "project_id": self.project.id,
                "unit_amount": 3,
                "employee_id": self.employee.id,
            }
        )
        self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(
                unit_amount=7,
                product_uom_id=self.env.ref(
                    "project_consumable.uom_cat_coffee_capsule_box_10"
                ).id,
            )
        )
        analysis = self.env["timesheets.analysis.report"].search(
            [
                ("project_id", "=", self.project.id),
                ("employee_id", "=", self.employee.id),
            ]
        )
        self.assertEqual(len(analysis), 1)
        self.assertEqual(analysis.unit_amount, 3)

    def test_timesheet_attendance_report_with_consumable(self):
        self.env["account.analytic.line"].with_user(self.user_demo).create(
            {
                "name": "Test timesheet 1",
                "project_id": self.project.id,
                "unit_amount": 6.0,
                "date": datetime(2022, 2, 9),
            }
        )
        self.env["account.analytic.line"].create(
            self._prepare_consumable_line_data(
                unit_amount=7,
                product_uom_id=self.env.ref(
                    "project_consumable.uom_cat_coffee_capsule_box_10"
                ).id,
                employee_id=self.employee.id,
                date=datetime(2022, 2, 9),
            )
        )
        total_timesheet, total_attendance = self.env[
            "hr.timesheet.attendance.report"
        ]._read_group(
            [
                ("employee_id", "=", self.employee.id),
                ("date", ">=", datetime(2022, 2, 9, 8, 0)),
                ("date", "<=", datetime(2022, 2, 9, 16, 0)),
            ],
            aggregates=["total_timesheet:sum", "total_attendance:sum"],
        )[0]
        self.assertEqual(
            total_timesheet, 6.0, "Total timesheet in report should be 4.0"
        )
        self.assertEqual(
            total_attendance, 7.0, "Total attendance in report should be 8.0"
        )
        self.assertEqual(total_attendance - total_timesheet, 1)
