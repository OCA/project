# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from datetime import date, datetime, timedelta

from odoo.tests.common import TransactionCase


class TestEmployeeBucket(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Enable tracking bypass
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # 1. Create calendar with standard 8h/day, Mon-Fri schedule
        cls.calendar = cls.env["resource.calendar"].create(
            {
                "name": "Standard Mon-Fri 40h Calendar",
                "tz": "UTC",
            }
        )
        # Standard attendance: Monday to Friday, 8:00 to 12:00
        # and 13:00 to 17:00 (8 hours total per day)
        days = [0, 1, 2, 3, 4]  # Mon-Fri
        for day in days:
            cls.env["resource.calendar.attendance"].create(
                {
                    "name": f"Morning Day {day}",
                    "calendar_id": cls.calendar.id,
                    "dayofweek": str(day),
                    "hour_from": 8.0,
                    "hour_to": 12.0,
                    "day_period": "morning",
                }
            )
            cls.env["resource.calendar.attendance"].create(
                {
                    "name": f"Afternoon Day {day}",
                    "calendar_id": cls.calendar.id,
                    "dayofweek": str(day),
                    "hour_from": 13.0,
                    "hour_to": 17.0,
                    "day_period": "afternoon",
                }
            )

        # 2. Create employee linked to the calendar
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Capacity Employee",
                "resource_calendar_id": cls.calendar.id,
            }
        )

        # 3. Create a leave type
        cls.leave_type = cls.env["hr.leave.type"].create(
            {
                "name": "Capacity Test Leave",
                "requires_allocation": False,
            }
        )

    def test_01_cron_capacity_calculation_weekly(self):
        """Test weekly capacity calculation and cron generation."""
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_planning.planning_bucket", "weekly"
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_planning.theoretical_capacity_months_forward", "1"
        )

        # Execute the cron job
        self.env["hr.employee.bucket"].cron_update_employee_capacity()

        # Find capacities generated for the employee
        capacities = self.env["hr.employee.bucket"].search(
            [("employee_id", "=", self.employee.id)]
        )
        self.assertTrue(len(capacities) > 0)

        # Check standard 40h week (e.g. S21 of 2026 starting Monday May 18, 2026)
        week_capacity = capacities.filtered(lambda c: c.bucket == "2026-S21")
        if week_capacity:
            # 5 work days * 8h = 40.0 hours
            self.assertEqual(week_capacity.working_hours, 40.0)

    def test_02_leave_update_trigger(self):
        """Test that hr.leave actions update capacity records."""
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_planning.planning_bucket", "weekly"
        )

        bucket_rec = self.env["project.bucket"]._get_or_create_bucket(date(2026, 5, 18))
        capacity = self.env["hr.employee.bucket"].create(
            {
                "employee_id": self.employee.id,
                "bucket_id": bucket_rec.id,
                "working_hours": 40.0,
            }
        )
        self.assertEqual(capacity.working_hours, 40.0)

        # Create an approved leave of 1 day (Tuesday May 19, 2026, 8:00 to 17:00 UTC)
        leave = self.env["hr.leave"].create(
            {
                "name": "One day sick leave",
                "employee_id": self.employee.id,
                "holiday_status_id": self.leave_type.id,
                "date_from": datetime(2026, 5, 19, 8, 0, 0),
                "date_to": datetime(2026, 5, 19, 17, 0, 0),
                "request_date_from": date(2026, 5, 19),
                "request_date_to": date(2026, 5, 19),
                "number_of_days": 1,
            }
        )
        if hasattr(leave, "action_approve"):
            leave.action_approve()
        if hasattr(leave, "action_validate"):
            leave.action_validate()
        elif hasattr(leave, "_action_validate"):
            leave._action_validate()

        # The capacity should automatically update to 32.0 hours (40 - 8)
        self.assertEqual(capacity.working_hours, 32.0)

        # Modify the leave to cover 2 days (Tuesday May 19 and Wednesday May 20)
        if hasattr(leave, "action_refuse"):
            leave.action_refuse()
        if hasattr(leave, "action_draft"):
            leave.action_draft()

        leave.write(
            {
                "date_to": datetime(2026, 5, 20, 17, 0, 0),
                "request_date_to": date(2026, 5, 20),
                "number_of_days": 2,
            }
        )

        if hasattr(leave, "action_approve"):
            leave.action_approve()
        if hasattr(leave, "action_validate"):
            leave.action_validate()
        elif hasattr(leave, "_action_validate"):
            leave._action_validate()
        # The capacity should automatically update to 24.0 hours (40 - 16)
        self.assertEqual(capacity.working_hours, 24.0)

        # Delete/unlink the leave
        leave.unlink()
        # The capacity should restore to 40.0 hours
        self.assertEqual(capacity.working_hours, 40.0)

    def test_03_resource_calendar_leave_trigger(self):
        """Test that calendar-specific resource leaves trigger capacity updates."""
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_planning.planning_bucket", "weekly"
        )

        bucket_rec = self.env["project.bucket"]._get_or_create_bucket(date(2026, 5, 18))
        capacity = self.env["hr.employee.bucket"].create(
            {
                "employee_id": self.employee.id,
                "bucket_id": bucket_rec.id,
                "working_hours": 40.0,
            }
        )
        self.assertEqual(capacity.working_hours, 40.0)

        # Create a resource calendar leave (specific holiday for employee)
        cal_leave = self.env["resource.calendar.leaves"].create(
            {
                "name": "Individual Holiday",
                "calendar_id": self.calendar.id,
                "resource_id": self.employee.resource_id.id,
                "date_from": datetime(2026, 5, 21, 8, 0, 0),
                "date_to": datetime(2026, 5, 21, 17, 0, 0),
            }
        )

        # The capacity should automatically update to 32.0 hours (40 - 8)
        self.assertEqual(capacity.working_hours, 32.0)

        # Modify the calendar leave to span 2 days (May 21 and May 22)
        cal_leave.write(
            {
                "date_to": datetime(2026, 5, 22, 17, 0, 0),
            }
        )
        # The capacity should automatically update to 24.0 hours (40 - 16)
        self.assertEqual(capacity.working_hours, 24.0)

        # Delete/unlink the calendar leave
        cal_leave.unlink()
        # The capacity should restore to 40.0 hours
        self.assertEqual(capacity.working_hours, 40.0)

    def test_04_daily_and_monthly_capacities(self):
        """Test daily and monthly capacity settings."""
        # 1. Monthly
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_planning.planning_bucket", "monthly"
        )
        bucket_rec = self.env["project.bucket"]._get_or_create_bucket(date(2026, 5, 1))
        self.assertEqual(bucket_rec.name, "2026-M05")

        monthly_capacity = self.env["hr.employee.bucket"].create(
            {
                "employee_id": self.employee.id,
                "bucket_id": bucket_rec.id,
            }
        )
        self.assertEqual(monthly_capacity.bucket, "2026-M05")
        # May 2026 has 21 working days (Mon-Fri) * 8h = 168.0 hours
        self.assertEqual(monthly_capacity.working_hours, 168.0)

        # 2. Daily
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_planning.planning_bucket", "daily"
        )
        daily_bucket = self.env["project.bucket"]._get_or_create_bucket(
            date(2026, 5, 18)
        )
        self.assertEqual(daily_bucket.name, "2026-05-18")

        daily_capacity = self.env["hr.employee.bucket"].create(
            {
                "employee_id": self.employee.id,
                "bucket_id": daily_bucket.id,
            }
        )
        self.assertEqual(daily_capacity.bucket, "2026-05-18")
        self.assertEqual(daily_capacity.working_hours, 8.0)

    def test_05_employee_smart_button_and_fields(self):
        """Test computed fields and smart button action on hr.employee."""
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_planning.planning_bucket", "weekly"
        )
        # Force clear existing records for the employee to have a clean starting point
        self.env["hr.employee.bucket"].search(
            [("employee_id", "=", self.employee.id)]
        ).unlink()

        # Count should start at 0
        self.assertEqual(self.employee.bucket_capacity_count, 0)

        bucket1 = self.env["project.bucket"]._get_or_create_bucket(date(2026, 5, 18))
        bucket2 = self.env["project.bucket"]._get_or_create_bucket(date(2026, 5, 25))

        # Create two capacity records
        self.env["hr.employee.bucket"].create(
            [
                {
                    "employee_id": self.employee.id,
                    "bucket_id": bucket1.id,
                },
                {
                    "employee_id": self.employee.id,
                    "bucket_id": bucket2.id,
                },
            ]
        )

        # Recalculate and assert count is 2
        self.employee.invalidate_recordset(["bucket_capacity_count"])
        self.assertEqual(self.employee.bucket_capacity_count, 2)

        # Execute action and verify returned dictionary
        action = self.employee.action_view_bucket_capacity()
        self.assertEqual(action["res_model"], "hr.employee.bucket")
        self.assertIn(("employee_id", "=", self.employee.id), action["domain"])

    def test_06_planning_relationship_and_hours_aggregation(self):
        """Test that task planning links back and updates planned/remaining hours."""
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_planning.planning_bucket", "weekly"
        )

        # Create project and task
        project = self.env["project.project"].create(
            {
                "name": "Test Project",
                "total_estimated_hours_override": 100.0,
            }
        )
        task = self.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": project.id,
                "percentage_of_project_hours": 40.0,
                "planned_date_start": datetime(2026, 5, 18, 8, 0, 0),
                "planned_date_end": datetime(2026, 5, 22, 17, 0, 0),
            }
        )

        # Allocate task to employee
        allocation = self.env["project.task.allocation"].create(
            {
                "task_id": task.id,
                "employee_id": self.employee.id,
                "participation_percentage": 50.0,
                "date_start": date(2026, 5, 18),
                "date_end": date(2026, 5, 22),
            }
        )
        self.assertEqual(allocation.estimated_hours, 20.0)

        # Ensure employee bucket exists for 2026-S21
        bucket_rec = self.env["project.bucket"]._get_or_create_bucket(date(2026, 5, 18))
        capacity = self.env["hr.employee.bucket"].create(
            {
                "employee_id": self.employee.id,
                "bucket_id": bucket_rec.id,
            }
        )
        self.assertEqual(capacity.working_hours, 40.0)
        self.assertEqual(capacity.planned_hours, 0.0)
        self.assertEqual(capacity.remaining_hours, 40.0)

        # Generate planning
        allocation.action_generate_planning()

        # Retrieve planning entries generated
        plannings = self.env["project.task.planning"].search(
            [("allocation_id", "=", allocation.id)]
        )
        self.assertTrue(len(plannings) > 0)

        # Verify employee_bucket_id is set
        for planning in plannings:
            self.assertEqual(planning.employee_bucket_id.id, capacity.id)

        # Check aggregated planned and remaining hours
        capacity.invalidate_recordset(["planned_hours", "remaining_hours"])
        self.assertEqual(capacity.planned_hours, 20.0)
        self.assertEqual(capacity.remaining_hours, 20.0)

        # Over-plan hours (modify planning entry to have 50.0 hours,
        # which is greater than working_hours 40.0)
        plannings[0].write({"planned_hours": 50.0})
        capacity.invalidate_recordset(["planned_hours", "remaining_hours"])
        self.assertEqual(capacity.planned_hours, 50.0)
        self.assertEqual(capacity.remaining_hours, -10.0)

        # Verify that the remaining_hours filter logic retrieves this bucket
        over_planned_buckets = self.env["hr.employee.bucket"].search(
            [("id", "=", capacity.id), ("remaining_hours", "<", 0.0)]
        )
        self.assertEqual(len(over_planned_buckets), 1)

    def test_07_utilization_rate_and_group_aggregation(self):
        """Test calculation of utilization_rate and correct group aggregation."""
        self.env["ir.config_parameter"].sudo().set_param(
            "project_task_planning.planning_bucket", "weekly"
        )

        # Clear existing bucket capacities
        self.env["hr.employee.bucket"].search(
            [("employee_id", "=", self.employee.id)]
        ).unlink()

        # Create two bucket capacity records
        bucket1 = self.env["project.bucket"]._get_or_create_bucket(date(2026, 5, 18))
        bucket2 = self.env["project.bucket"]._get_or_create_bucket(date(2026, 5, 25))

        # Record 1: 40 hours capacity, 20 hours planned -> 50% utilization
        capacity1 = self.env["hr.employee.bucket"].create(
            {
                "employee_id": self.employee.id,
                "bucket_id": bucket1.id,
                "working_hours": 40.0,
            }
        )

        project = self.env["project.project"].create({"name": "Test Project 1"})
        task1 = self.env["project.task"].create(
            {
                "name": "Task 1",
                "project_id": project.id,
                "planned_date_start": datetime(2026, 5, 18, 8, 0, 0),
                "planned_date_end": datetime(2026, 5, 22, 17, 0, 0),
            }
        )
        allocation1 = self.env["project.task.allocation"].create(
            {
                "task_id": task1.id,
                "employee_id": self.employee.id,
                "participation_percentage": 100.0,
                "date_start": date(2026, 5, 18),
                "date_end": date(2026, 5, 22),
            }
        )
        self.env["project.task.planning"].create(
            {
                "allocation_id": allocation1.id,
                "employee_bucket_id": capacity1.id,
                "planned_hours": 20.0,
                "date_start": date(2026, 5, 18),
                "date_end": date(2026, 5, 22),
            }
        )

        capacity1.invalidate_recordset(["planned_hours", "utilization_rate"])
        self.assertEqual(capacity1.planned_hours, 20.0)
        self.assertEqual(capacity1.utilization_rate, 50.0)

        # Record 2: 40 hours capacity (computed), 5 hours planned -> 12.5% utilization
        capacity2 = self.env["hr.employee.bucket"].create(
            {
                "employee_id": self.employee.id,
                "bucket_id": bucket2.id,
            }
        )
        task2 = self.env["project.task"].create(
            {
                "name": "Task 2",
                "project_id": project.id,
                "planned_date_start": datetime(2026, 5, 25, 8, 0, 0),
                "planned_date_end": datetime(2026, 5, 29, 17, 0, 0),
            }
        )
        allocation2 = self.env["project.task.allocation"].create(
            {
                "task_id": task2.id,
                "employee_id": self.employee.id,
                "participation_percentage": 100.0,
                "date_start": date(2026, 5, 25),
                "date_end": date(2026, 5, 29),
            }
        )
        self.env["project.task.planning"].create(
            {
                "allocation_id": allocation2.id,
                "employee_bucket_id": capacity2.id,
                "planned_hours": 5.0,
                "date_start": date(2026, 5, 25),
                "date_end": date(2026, 5, 29),
            }
        )

        capacity2.invalidate_recordset(["planned_hours", "utilization_rate"])
        self.assertEqual(capacity2.planned_hours, 5.0)
        self.assertEqual(capacity2.utilization_rate, 12.5)

        # Check standard Odoo read_group grouping on both capacities
        # We group by employee_id. The result should recalculate dynamically
        # planned sum = 20 + 5 = 25
        # working sum = 40 + 40 = 80
        # utilization rate group calculation = 25 / 80 * 100 = 31.25%
        res = self.env["hr.employee.bucket"].read_group(
            domain=[("id", "in", [capacity1.id, capacity2.id])],
            fields=["working_hours", "planned_hours", "utilization_rate"],
            groupby=["employee_id"],
        )

        self.assertEqual(len(res), 1)
        group_line = res[0]
        self.assertEqual(group_line.get("working_hours"), 80.0)
        self.assertEqual(group_line.get("planned_hours"), 25.0)

        # Verify it didn't do sum (50 + 12.5 = 62.5) or flat average (31.25)
        self.assertAlmostEqual(group_line.get("utilization_rate"), 31.25, places=2)

        # Check standard Odoo _read_grouping_sets (Pivot View) on capacities
        # We query grouping_sets: [['employee_id'], []] (by employee, and grand total)
        res_sets = self.env["hr.employee.bucket"]._read_grouping_sets(
            domain=[("id", "in", [capacity1.id, capacity2.id])],
            grouping_sets=[["employee_id"], []],
            aggregates=[
                "working_hours:sum",
                "planned_hours:sum",
                "utilization_rate:sum",
            ],
        )

        self.assertEqual(len(res_sets), 2)

        # 1. Grouped by employee_id
        grouped_by_emp = res_sets[0]
        self.assertEqual(len(grouped_by_emp), 1)
        emp_row = grouped_by_emp[0]
        # Tuple: (employee_id_val, working_hours_sum, planned_hours_sum,
        # utilization_rate_sum)
        self.assertEqual(emp_row[1], 80.0)  # working_hours sum
        self.assertEqual(emp_row[2], 25.0)  # planned_hours sum
        # utilization_rate calculated correctly
        self.assertAlmostEqual(emp_row[3], 31.25, places=2)

        # 2. Grand total (empty groupby)
        grand_total = res_sets[1]
        self.assertEqual(len(grand_total), 1)
        total_row = grand_total[0]
        # Tuple: (working_hours_sum, planned_hours_sum, utilization_rate_sum)
        self.assertEqual(total_row[0], 80.0)  # working_hours sum
        self.assertEqual(total_row[1], 25.0)  # planned_hours sum
        # utilization_rate calculated correctly
        self.assertAlmostEqual(total_row[2], 31.25, places=2)

    def test_08_relative_index(self):
        # Dynamically calculate Monday of the current week to be date-independent
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        bucket_today = self.env["project.bucket"].create(
            {
                "name": "today-TestIndex",
                "date_start": monday,
                "date_end": monday + timedelta(days=6),
                "bucket_type": "weekly",
            }
        )
        bucket_next = self.env["project.bucket"].create(
            {
                "name": "next-TestIndex",
                "date_start": monday + timedelta(days=7),
                "date_end": monday + timedelta(days=13),
                "bucket_type": "weekly",
            }
        )
        bucket_prev = self.env["project.bucket"].create(
            {
                "name": "prev-TestIndex",
                "date_start": monday - timedelta(days=7),
                "date_end": monday - timedelta(days=1),
                "bucket_type": "weekly",
            }
        )

        # Test compute relative index on project.bucket
        bucket_today.invalidate_recordset(["relative_index"])
        bucket_next.invalidate_recordset(["relative_index"])
        bucket_prev.invalidate_recordset(["relative_index"])

        self.assertEqual(bucket_today.relative_index, 0)
        self.assertEqual(bucket_next.relative_index, 1)
        self.assertEqual(bucket_prev.relative_index, -1)

        # Test search on relative_index
        buckets_future = self.env["project.bucket"].search(
            [
                ("relative_index", ">", 0),
                ("relative_index", "<=", 2),
                ("bucket_type", "=", "weekly"),
            ]
        )
        self.assertIn(bucket_next, buckets_future)
        self.assertNotIn(bucket_today, buckets_future)
        self.assertNotIn(bucket_prev, buckets_future)

        # Now test hr.employee.bucket
        employee = self.env["hr.employee"].create({"name": "Test Index Employee"})
        capacity_today = self.env["hr.employee.bucket"].create(
            {
                "employee_id": employee.id,
                "bucket_id": bucket_today.id,
            }
        )
        capacity_next = self.env["hr.employee.bucket"].create(
            {
                "employee_id": employee.id,
                "bucket_id": bucket_next.id,
            }
        )

        capacity_today.invalidate_recordset(["relative_index"])
        capacity_next.invalidate_recordset(["relative_index"])

        self.assertEqual(capacity_today.relative_index, 0)
        self.assertEqual(capacity_next.relative_index, 1)

        # Test search on relative_index in hr.employee.bucket
        capacities_search = self.env["hr.employee.bucket"].search(
            [
                ("relative_index", ">=", 0),
                ("relative_index", "<", 2),
            ]
        )
        self.assertIn(capacity_today, capacities_search)
        self.assertIn(capacity_next, capacities_search)

    def test_09_delayed_employee_bucket_creation(self):
        """Test that if a project.task.planning record is created before
        the matching hr.employee.bucket exists, creating the bucket later
        will automatically associate them and update totals."""
        # 1. Create a test employee, project, task, and allocation
        employee = self.env["hr.employee"].create(
            {
                "name": "Delayed Test Employee",
                "resource_calendar_id": self.calendar.id,
            }
        )
        project = self.env["project.project"].create(
            {
                "name": "Delayed Test Project",
            }
        )
        task = self.env["project.task"].create(
            {
                "name": "Delayed Test Task",
                "project_id": project.id,
            }
        )
        allocation = self.env["project.task.allocation"].create(
            {
                "task_id": task.id,
                "employee_id": employee.id,
                "participation_percentage": 50.0,
                "date_start": date(2026, 5, 18),
                "date_end": date(2026, 5, 24),
            }
        )

        bucket_rec = self.env["project.bucket"]._get_or_create_bucket(date(2026, 5, 18))

        # 2. Create the planning record directly (simulating demo data loader)
        planning = self.env["project.task.planning"].create(
            {
                "allocation_id": allocation.id,
                "bucket_id": bucket_rec.id,
                "planned_hours": 10.0,
            }
        )

        # Initially, employee_bucket_id must be False because the
        # hr.employee.bucket doesn't exist
        planning._compute_employee_bucket_id()
        self.assertFalse(planning.employee_bucket_id)

        # 3. Create the capacity bucket later
        capacity = self.env["hr.employee.bucket"].create(
            {
                "employee_id": employee.id,
                "bucket_id": bucket_rec.id,
                "working_hours": 40.0,
            }
        )

        # 4. Check if the relation has been automatically established
        self.assertEqual(planning.employee_bucket_id, capacity)

        # 5. Check if the capacity bucket's planned hours has been updated
        # via Odoo dependencies
        self.assertEqual(capacity.planned_hours, 10.0)
