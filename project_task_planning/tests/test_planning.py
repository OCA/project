# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from datetime import date

from psycopg2 import IntegrityError

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProjectTaskPlanning(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Clean context and disable tracking to speed up tests
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Create a test employee
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Technician",
            }
        )

        # Create a test project with target estimated hours
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "total_estimated_hours_override": 100.0,
                "date_start": date(2026, 5, 1),
                "date": date(2026, 5, 31),
            }
        )

        # Create a test task with timeline planned dates
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
                "percentage_of_project_hours": 40.0,  # 40% of the project total hours
                "planned_date_start": date(2026, 5, 11),
                "planned_date_end": date(2026, 5, 24),  # 2 weeks duration
            }
        )

    def test_01_project_task_scaling(self):
        """Test task-level project percentage calculation."""
        self.assertEqual(self.task.project_percentage, 0.40)
        self.assertEqual(self.task.percentage_of_project_hours, 40.0)

    def test_02_task_allocation_and_planning_weekly(self):
        """Test generating allocation and weekly planning entries."""
        # Set system parameter to 'weekly'
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_planning.planning_bucket", "weekly"
        )

        # Link task to employee user to allow auto-allocation
        self.employee.user_id = self.env.user.id
        self.task.user_ids = [(4, self.env.user.id)]

        # Generate allocation
        self.task.action_generate_allocation()
        self.assertEqual(len(self.task.allocation_ids), 1)

        allocation = self.task.allocation_ids[0]
        self.assertEqual(allocation.employee_id, self.employee)
        self.assertEqual(allocation.estimated_hours, 40.0)
        self.assertEqual(allocation.pending_to_plan_hours, 40.0)

        # Generate Planning
        self.task.action_generate_planning()
        plannings = allocation.planning_ids
        # Since date_start=2026-05-11 (Monday) and date_end=2026-05-24 (Sunday)
        # Period has 14 days, which is exactly 2 full weeks
        self.assertEqual(len(plannings), 2)

        # Check total planned hours
        self.assertEqual(sum(plannings.mapped("planned_hours")), 40.0)
        for p in plannings:
            self.assertEqual(p.planned_hours, 20.0)
            self.assertTrue(p.bucket.startswith("2026-S"))

        # Verify task list / smart buttons
        action = self.task.action_view_planning()
        self.assertEqual(action["domain"], [("task_id", "=", self.task.id)])

        action_project = self.project.action_view_planning()
        self.assertEqual(
            action_project["domain"], [("project_id", "=", self.project.id)]
        )

        # Verify custom display values for Task Smart Button
        self.task._compute_planning_displays()
        self.assertEqual(self.task.planning_total_display, "40:00")
        self.assertEqual(self.task.planning_planned_display, "40:00")
        self.assertEqual(self.task.planning_pct_display, "100.0%")

        # Verify custom display values for Project Smart Button
        self.project._compute_planning_displays()
        self.assertEqual(self.project.planning_total_display, "100:00")
        self.assertEqual(self.project.planning_planned_display, "40:00")
        self.assertEqual(self.project.planning_pct_display, "40.0%")

    def test_03_planning_daily(self):
        """Test daily planning bucket configuration."""
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_planning.planning_bucket", "daily"
        )

        # Create allocation manually
        allocation = self.env["project.task.allocation"].create(
            {
                "task_id": self.task.id,
                "employee_id": self.employee.id,
                "participation_percentage": 50.0,
                "date_start": date(2026, 5, 11),
                "date_end": date(2026, 5, 15),  # 5 days
            }
        )

        self.assertEqual(allocation.estimated_hours, 20.0)

        # Generate planning
        allocation.action_generate_planning()
        plannings = allocation.planning_ids
        self.assertEqual(len(plannings), 5)
        self.assertEqual(sum(plannings.mapped("planned_hours")), 20.0)
        for p in plannings:
            self.assertEqual(p.planned_hours, 4.0)
            self.assertEqual(p.bucket, p.date_start.strftime("%Y-%m-%d"))

    def test_04_planning_monthly(self):
        """Test monthly planning bucket configuration."""
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_planning.planning_bucket", "monthly"
        )

        # Create allocation spanning parts of two months
        allocation = self.env["project.task.allocation"].create(
            {
                "task_id": self.task.id,
                "employee_id": self.employee.id,
                "participation_percentage": 100.0,
                "date_start": date(2026, 5, 25),  # 7 days in May
                "date_end": date(2026, 6, 3),  # 3 days in June (total 10 days)
            }
        )

        self.assertEqual(allocation.estimated_hours, 40.0)

        # Generate planning
        allocation.action_generate_planning()
        plannings = allocation.planning_ids
        self.assertEqual(len(plannings), 2)
        self.assertEqual(sum(plannings.mapped("planned_hours")), 40.0)

        may_planning = plannings.filtered(lambda p: p.bucket == "2026-M05")
        june_planning = plannings.filtered(lambda p: p.bucket == "2026-M06")

        self.assertEqual(len(may_planning), 1)
        self.assertEqual(len(june_planning), 1)

        # May has 7 days, so 7 * 4.0 = 28.0 hours
        self.assertAlmostEqual(may_planning.planned_hours, 28.0)
        # June has 3 days, so 3 * 4.0 = 12.0 hours
        self.assertAlmostEqual(june_planning.planned_hours, 12.0)

    def test_05_constraint_and_warnings(self):
        """Test validation and constraints."""
        allocation = self.env["project.task.allocation"].create(
            {
                "task_id": self.task.id,
                "employee_id": self.employee.id,
                "participation_percentage": 100.0,
                "date_start": date(2026, 5, 11),
                "date_end": date(2026, 5, 24),
            }
        )

        # Test duplicate bucket constraint
        self.env["project.task.planning"].create(
            {
                "allocation_id": allocation.id,
                "date_start": date(2026, 5, 11),
                "planned_hours": 10.0,
            }
        )

        with self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.env["project.task.planning"].create(
                    {
                        "allocation_id": allocation.id,
                        "date_start": date(2026, 5, 12),  # Same week bucket
                        "planned_hours": 10.0,
                    }
                )

    def test_06_disable_planning(self):
        """Test disabling planning for an employee and associated constraints."""
        # 1. Test that setting disable_planning = True deletes existing employee buckets
        self.env["hr.employee.bucket"].cron_update_employee_capacity()
        existing_buckets = self.env["hr.employee.bucket"].search(
            [("employee_id", "=", self.employee.id)]
        )
        self.assertTrue(len(existing_buckets) > 0)

        self.employee.write({"disable_planning": True})
        remaining_buckets = self.env["hr.employee.bucket"].search(
            [("employee_id", "=", self.employee.id)]
        )
        self.assertEqual(len(remaining_buckets), 0)

        # 2. Test constraint on hr.employee.bucket manual creation
        bucket_rec = self.env["project.bucket"]._get_or_create_bucket(date(2026, 5, 11))
        with self.assertRaises(UserError):
            with self.env.cr.savepoint():
                self.env["hr.employee.bucket"].create(
                    {
                        "employee_id": self.employee.id,
                        "bucket_id": bucket_rec.id,
                        "working_hours": 40.0,
                    }
                )

        # 3. Test constraint on project.task.allocation creation
        with self.assertRaises(UserError):
            with self.env.cr.savepoint():
                self.env["project.task.allocation"].create(
                    {
                        "task_id": self.task.id,
                        "employee_id": self.employee.id,
                        "participation_percentage": 50.0,
                        "date_start": date(2026, 5, 11),
                        "date_end": date(2026, 5, 15),
                    }
                )

        # 4. Test action_generate_allocation checks
        self.employee.user_id = self.env.user.id
        self.task.user_ids = [(4, self.env.user.id)]
        with self.assertRaises(UserError):
            with self.env.cr.savepoint():
                self.task.action_generate_allocation()

        # 5. Test cron does not generate buckets for disabled employees
        self.employee.write({"disable_planning": False})
        self.env["hr.employee.bucket"].cron_update_employee_capacity()
        buckets_enabled = self.env["hr.employee.bucket"].search(
            [("employee_id", "=", self.employee.id)]
        )
        self.assertTrue(len(buckets_enabled) > 0)

        self.employee.write({"disable_planning": True})  # clears them again
        self.env["hr.employee.bucket"].cron_update_employee_capacity()
        buckets_disabled = self.env["hr.employee.bucket"].search(
            [("employee_id", "=", self.employee.id)]
        )
        self.assertEqual(len(buckets_disabled), 0)

    def test_07_manual_estimated_hours(self):
        """Test manually modifying estimated_hours on allocation."""
        allocation = self.env["project.task.allocation"].create(
            {
                "task_id": self.task.id,
                "employee_id": self.employee.id,
                "participation_percentage": 100.0,
                "date_start": date(2026, 5, 11),
                "date_end": date(2026, 5, 15),
            }
        )
        self.assertEqual(allocation.estimated_hours, 40.0)

        # Manually modify estimated_hours
        allocation.write({"estimated_hours": 15.0})
        # Verifying that the inverse method updated the participation_percentage
        self.assertAlmostEqual(allocation.participation_percentage, 37.5)
        self.assertEqual(allocation.estimated_hours, 15.0)

        # Now modify another field of the allocation, e.g. date_end
        allocation.write({"date_end": date(2026, 5, 16)})

        # The estimated_hours should remain 15.0, not be recalculated back to 40.0!
        self.assertEqual(allocation.estimated_hours, 15.0)
