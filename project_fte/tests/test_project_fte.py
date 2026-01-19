# Copyright 2025 APSL Nagarro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time
from psycopg2 import IntegrityError

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestProjectFte(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
            )
        )
        cls.user = cls.env.ref("base.user_admin")
        cls.Project = cls.env["project.project"]
        cls.Role = cls.env["project.role"]
        cls.FteLine = cls.env["project.fte.month.line"]
        cls.FteDist = cls.env["project.fte.profile.distribution"]
        cls.Wizard = cls.env["project.fte.mass.generator"]
        cls.Task = cls.env["project.task"]

        cls.project = cls.Project.create({"name": "Test FTE Project"})
        cls.role_dev = cls.Role.create({"name": "Developer"})
        cls.role_pm = cls.Role.create({"name": "Project Manager"})

        cls.time_type_billable = cls.env["project.time.type"].create(
            {
                "name": "Billable",
                "non_billable": False,
            }
        )
        cls.time_type_non_billable = cls.env["project.time.type"].create(
            {
                "name": "Billable",
                "non_billable": True,
            }
        )

    def test_01_creation_and_name_compute(self):
        fte_line = self.FteLine.create(
            {
                "project_id": self.project.id,
                "month": "1",
                "year": 2025,
            }
        )
        self.assertTrue(fte_line, "FTE Line should be created.")
        self.assertEqual(
            fte_line.name,
            "January 2025",
            "The name should be computed correctly.",
        )
        self.assertEqual(fte_line.fte_hours, 0.0, "Initial FTE hours should be zero.")

    def test_02_fte_hours_computation(self):
        fte_line = self.FteLine.create(
            {
                "project_id": self.project.id,
                "month": "2",
                "year": 2025,
                "profile_distribution_ids": [
                    (0, 0, {"role_id": self.role_dev.id, "profile_hours": 120}),
                    (0, 0, {"role_id": self.role_pm.id, "profile_hours": 40}),
                ],
            }
        )
        self.assertEqual(
            fte_line.fte_hours, 160.0, "Total FTE hours should be the sum of its lines."
        )
        fte_line.profile_distribution_ids[0].profile_hours = 100
        self.assertEqual(
            fte_line.fte_hours, 140.0, "Total should be updated after a line change."
        )

        fte_line.profile_distribution_ids = [
            (0, 0, {"role_id": self.role_dev.id, "profile_hours": 20})
        ]
        self.assertEqual(
            fte_line.fte_hours,
            160.0,
            "Total should be updated after adding a new line.",
        )

    def test_03_percentage_computation(self):
        fte_line = self.FteLine.create(
            {
                "project_id": self.project.id,
                "month": "3",
                "year": 2025,
            }
        )
        dist_dev = self.FteDist.create(
            {
                "month_line_id": fte_line.id,
                "role_id": self.role_dev.id,
                "profile_hours": 120,
            }
        )
        dist_pm = self.FteDist.create(
            {
                "month_line_id": fte_line.id,
                "role_id": self.role_pm.id,
                "profile_hours": 40,
            }
        )

        self.assertAlmostEqual(dist_dev.profile_hours_percentage, 0.75)
        self.assertAlmostEqual(dist_pm.profile_hours_percentage, 0.25)

        dist_dev.profile_hours = 0
        dist_pm.profile_hours = 0
        self.assertAlmostEqual(dist_dev.profile_hours_percentage, 0.0)
        self.assertAlmostEqual(dist_pm.profile_hours_percentage, 0.0)

    @mute_logger("odoo.sql_db")
    def test_04_sql_constraint(self):
        self.FteLine.create(
            {
                "project_id": self.project.id,
                "month": "4",
                "year": 2025,
            }
        )
        with self.assertRaises(IntegrityError):
            self.FteLine.create(
                {
                    "project_id": self.project.id,
                    "month": "4",
                    "year": 2025,
                }
            )

    def test_05_ondelete_cascade(self):
        project_to_delete = self.Project.create({"name": "To Be Deleted"})
        fte_line = self.FteLine.create(
            {
                "project_id": project_to_delete.id,
                "month": "5",
                "year": 2025,
            }
        )
        dist_line = self.FteDist.create(
            {
                "month_line_id": fte_line.id,
                "role_id": self.role_dev.id,
                "profile_hours": 10,
            }
        )
        fte_line_id = fte_line.id
        dist_line_id = dist_line.id
        fte_line.unlink()
        self.assertFalse(
            self.FteDist.browse(dist_line_id).exists(),
            "Distribution line should be deleted when its "
            "parent month line is deleted.",
        )
        self.assertFalse(
            self.FteLine.browse(fte_line_id).exists(),
            "Month line should be deleted.",
        )

        fte_line = self.FteLine.create(
            {
                "project_id": project_to_delete.id,
                "month": "6",
                "year": 2025,
            }
        )
        fte_line_id = fte_line.id
        project_to_delete.unlink()
        self.assertFalse(
            self.FteLine.browse(fte_line_id).exists(),
            "FTE month line should be deleted when its project is deleted.",
        )

    def test_06_distribution_without_discount(self):
        role = self.role_dev
        role.price_hour = 50
        milestone = self.env["project.milestone"].create(
            {
                "name": "Milestone Dev",
                "project_id": self.project.id,
                "project_role_id": role.id,
            }
        )
        self.Task.create(
            {
                "name": "Task 1",
                "project_id": self.project.id,
                "allocated_hours": 40,
                "milestone_id": milestone.id,
            }
        )
        self.Task.create(
            {
                "name": "Task 2",
                "project_id": self.project.id,
                "allocated_hours": 60,
                "milestone_id": milestone.id,
            }
        )

        self.project._compute_allocated_hours()

        wizard = self.Wizard.create(
            {
                "project_id": self.project.id,
                "date_from": fields.Date.to_date("2025-02-01"),
                "fte_hours": 100,
            }
        )

        result = wizard.compute_profile_distribution_from_milestones()
        new_wizard = self.Wizard.browse(result["res_id"])
        line = new_wizard.profile_distribution_ids[0]

        self.assertEqual(line.role_id, role)
        self.assertEqual(line.profile_hours, 100)
        self.assertEqual(line.profile_price_hour, 50)
        self.assertEqual(line.profile_price_amount, 5000)

    def test_07_load_from_milestones(self):
        milestone_role_1 = self.Role.create(
            {
                "name": "Analyst",
                "price_hour": 80,
            }
        )
        milestone_role_2 = self.Role.create(
            {
                "name": "Senior Analyst",
                "price_hour": 100,
            }
        )

        milestone_1 = self.env["project.milestone"].create(
            {
                "name": "Milestone 1",
                "project_id": self.project.id,
                "project_role_id": milestone_role_1.id,
            }
        )
        milestone_2 = self.env["project.milestone"].create(
            {
                "name": "Milestone 2",
                "project_id": self.project.id,
                "project_role_id": milestone_role_2.id,
            }
        )

        self.Task.create(
            {
                "name": "Task A",
                "project_id": self.project.id,
                "allocated_hours": 100,
                "milestone_id": milestone_1.id,
            }
        )
        self.Task.create(
            {
                "name": "Task A_1",
                "project_id": self.project.id,
                "allocated_hours": 60,
                "milestone_id": milestone_1.id,
            }
        )
        self.Task.create(
            {
                "name": "Task B",
                "project_id": self.project.id,
                "allocated_hours": 50,
                "milestone_id": milestone_2.id,
            }
        )
        self.Task.create(
            {
                "name": "Task B_1",
                "project_id": self.project.id,
                "allocated_hours": 60,
                "milestone_id": milestone_2.id,
            }
        )

        self.project._compute_allocated_hours()

        wizard = self.Wizard.create(
            {
                "project_id": self.project.id,
                "date_from": fields.Date.to_date("2025-01-01"),
                "fte_hours": 270,
            }
        )

        result = wizard.compute_profile_distribution_from_milestones()
        new_wizard = self.Wizard.browse(result["res_id"])

        distribution_lines = new_wizard.profile_distribution_ids
        self.assertEqual(len(distribution_lines), 2)

        for line in distribution_lines:
            if line.role_id == milestone_role_1:
                self.assertEqual(line.profile_hours, 160)
                self.assertEqual(line.profile_price_hour, 80)
                self.assertEqual(line.profile_price_amount, 12800)
            elif line.role_id == milestone_role_2:
                self.assertEqual(line.profile_hours, 110)
                self.assertEqual(line.profile_price_hour, 100)
                self.assertEqual(line.profile_price_amount, 11000)

        new_wizard.monthly_hours = 135
        new_wizard.discount = 0.1

        new_wizard._compute_date_to()
        new_wizard._compute_total_amount()
        new_wizard._compute_month_amount()

        self.assertEqual(
            new_wizard.date_to.month,
            fields.Date.to_date("2025-03-31").month,
            "should create 2 months",
        )
        self.assertAlmostEqual(new_wizard.fte_months, 2.0)

        self.assertEqual(new_wizard.total_raw_amount, 23800)
        self.assertEqual(new_wizard.total_amount, 23800 * 0.9)
        self.assertEqual(new_wizard.discount_amount, 23800 * 0.1)

        month_raw_total = new_wizard.total_raw_amount / (new_wizard.date_to.month - 1)

        self.assertAlmostEqual(new_wizard.month_raw_amount, month_raw_total)
        self.assertAlmostEqual(new_wizard.month_amount, month_raw_total * 0.9)
        self.assertAlmostEqual(new_wizard.month_discount_amount, month_raw_total * 0.1)

        self.assertEqual(result["res_model"], "project.fte.mass.generator")
        self.assertEqual(result["res_id"], wizard.id)
        self.assertEqual(result["view_mode"], "form")

        new_wizard.action_generate_lines()

        fte_lines = self.FteLine.search([("project_id", "=", self.project.id)])
        self.assertTrue(fte_lines)

        self.assertAlmostEqual(self.project.total_raw_amount, wizard.total_raw_amount)
        self.assertAlmostEqual(self.project.discount_amount, wizard.discount_amount)
        self.assertAlmostEqual(self.project.total_amount, wizard.total_amount)
        self.assertAlmostEqual(self.project.fte_months, 2.0)

        self.assertAlmostEqual(self.project.monthly_raw_amount, wizard.month_raw_amount)
        self.assertAlmostEqual(
            self.project.monthly_discount_amount, wizard.month_discount_amount
        )
        self.assertAlmostEqual(self.project.monthly_amount, wizard.month_amount)

        self.assertEqual(len(self.project.fte_month_line_ids), 2)
        self.project.action_copy_last_fte_line()
        self.assertEqual(len(self.project.fte_month_line_ids), 3)

    def test_08_executed_hours_and_percent(self):
        AccountAnalyticLine = self.env["account.analytic.line"]

        fte_line = self.FteLine.create(
            {
                "fte_hours": 100,
                "project_id": self.project.id,
                "month": "7",
                "year": 2025,
                "profile_distribution_ids": [
                    (0, 0, {"role_id": self.role_dev.id, "profile_hours": 100}),
                ],
            }
        )

        self.assertEqual(fte_line.executed_hours, 0.0)
        self.assertEqual(fte_line.executed_percent, 0.0)

        line = AccountAnalyticLine.create(
            {
                "name": "Timesheet A",
                "project_id": self.project.id,
                "unit_amount": 40,
                "date": fields.Date.to_date("2025-07-15"),
                "user_id": self.user.id,
                "time_type_id": self.time_type_billable.id,
            }
        )

        fte_line._compute_executed_hours()
        fte_line._compute_executed_percent()
        self.assertEqual(fte_line.executed_hours, 40)
        self.assertEqual(fte_line.executed_percent, 40)

        AccountAnalyticLine.create(
            {
                "name": "Timesheet B",
                "project_id": self.project.id,
                "unit_amount": 99,
                "date": fields.Date.to_date("2025-08-01"),
                "user_id": self.user.id,
                "time_type_id": self.time_type_billable.id,
            }
        )
        fte_line._compute_executed_hours()
        fte_line._compute_executed_percent()
        self.assertEqual(fte_line.executed_hours, 40)
        self.assertEqual(fte_line.executed_percent, 40)

        line.write({"unit_amount": 60})

        fte_line._compute_executed_hours()
        fte_line._compute_executed_percent()
        self.assertEqual(fte_line.executed_hours, 60)
        self.assertEqual(fte_line.executed_percent, 60)

        line.unlink()
        self.assertEqual(fte_line.executed_hours, 0.0)
        self.assertEqual(fte_line.executed_percent, 0.0)

        AccountAnalyticLine.create(
            {
                "name": "Timesheet Non Billable",
                "project_id": self.project.id,
                "unit_amount": 10,
                "date": fields.Date.to_date("2025-08-01"),
                "user_id": self.user.id,
                "time_type_id": self.time_type_non_billable.id,
            }
        )

        fte_line._compute_executed_hours()
        fte_line._compute_executed_percent()
        self.assertEqual(fte_line.executed_hours, 0.0)

    @freeze_time("2025-07-16")
    def test_09_test_cron_warning_state(self):
        AccountAnalyticLine = self.env["account.analytic.line"]
        fte_line = self.FteLine.create(
            {
                "fte_hours": 100,
                "project_id": self.project.id,
                "month": "7",
                "year": 2025,
                "profile_distribution_ids": [
                    (0, 0, {"role_id": self.role_dev.id, "profile_hours": 100}),
                ],
            }
        )

        self.assertFalse(
            not fte_line.high_usage_sent
            and not fte_line.warning_sent
            and fte_line.overload_sent,
        )

        AccountAnalyticLine.create(
            {
                "name": "Timesheet A",
                "project_id": self.project.id,
                "unit_amount": 20,
                "date": fields.Date.to_date("2025-07-16"),
                "user_id": self.user.id,
                "time_type_id": self.time_type_billable.id,
            }
        )

        fte_line._compute_executed_hours()
        fte_line._compute_executed_percent()
        fte_line._cron_check_fte_execution()
        self.assertTrue(fte_line.warning_sent)
        AccountAnalyticLine.create(
            {
                "name": "Timesheet B",
                "project_id": self.project.id,
                "unit_amount": 60,
                "date": fields.Date.to_date("2025-07-16"),
                "user_id": self.user.id,
                "time_type_id": self.time_type_billable.id,
            }
        )

        fte_line._compute_executed_hours()
        fte_line._compute_executed_percent()
        fte_line._cron_check_fte_execution()
        self.assertTrue(fte_line.high_usage_sent)

        AccountAnalyticLine.create(
            {
                "name": "Timesheet C",
                "project_id": self.project.id,
                "unit_amount": 50,
                "date": fields.Date.to_date("2025-07-16"),
                "user_id": self.user.id,
                "time_type_id": self.time_type_billable.id,
            }
        )
        fte_line._compute_executed_hours()
        fte_line._compute_executed_percent()
        fte_line._cron_check_fte_execution()
        self.assertTrue(fte_line.overload_sent)

    def test_10_fte_with_fixed_hours(self):
        AccountAnalyticLine = self.env["account.analytic.line"]
        role = self.role_dev
        role.price_hour = 50

        self.project._compute_allocated_hours()

        wizard = self.Wizard.create(
            {
                "project_id": self.project.id,
                "date_from": fields.Date.to_date("2025-02-01"),
                "fte_hours": 100,
                "monthly_hours": 100,
                "fixed_hours": 20.0,
                "fixed_hours_cost": 50.0,
                "profile_distribution_ids": [
                    (0, 0, {"role_id": role.id, "profile_hours": 100}),
                ],
            }
        )
        expected_raw_total = (wizard.fte_hours * role.price_hour) + (
            wizard.fixed_hours * wizard.fixed_hours_cost
        )
        self.assertEqual(wizard.total_raw_amount, expected_raw_total)
        wizard.discount = 0.25
        discount = expected_raw_total * wizard.discount
        expected_total = expected_raw_total - discount
        self.assertEqual(wizard.total_amount, expected_total)
        self.assertEqual(wizard.discount_amount, discount)
        wizard.action_generate_lines()

        AccountAnalyticLine.create(
            {
                "name": "Timesheet A",
                "project_id": self.project.id,
                "unit_amount": 50,
                "date": fields.Date.to_date("2025-02-15"),
                "user_id": self.user.id,
                "time_type_id": self.time_type_billable.id,
            }
        )
        fte_line = self.FteLine.search(
            [
                ("project_id", "=", self.project.id),
                ("month", "=", "2"),
                ("year", "=", 2025),
            ]
        )
        self.assertAlmostEqual(fte_line.executed_hours, 30)
