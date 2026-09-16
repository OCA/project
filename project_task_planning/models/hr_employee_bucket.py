# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from datetime import timedelta, timezone

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class EmployeeBucket(models.Model):
    _name = "hr.employee.bucket"
    _description = "Employee Bucket"
    _order = "employee_id, date_start desc"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade")
    bucket_id = fields.Many2one(
        "project.bucket", string="Planning Bucket", required=True, ondelete="cascade"
    )
    date_start = fields.Date(
        related="bucket_id.date_start", store=True, string="Start Date"
    )
    date_end = fields.Date(related="bucket_id.date_end", store=True, string="End Date")
    bucket = fields.Char(related="bucket_id.name", store=True)

    relative_index = fields.Integer(
        compute="_compute_relative_index",
        search="_search_relative_index",
        help=(
            "Chronological distance from the current period (0 for today's "
            "period, positive for future, negative for past)."
        ),
    )

    def _compute_relative_index(self):
        today = fields.Date.context_today(self)
        for record in self:
            if not record.date_start or not record.bucket_id.bucket_type:
                record.relative_index = 0
                continue
            today_start = self.env["project.bucket"]._get_bucket_start_date(
                today, record.bucket_id.bucket_type
            )
            if record.bucket_id.bucket_type == "daily":
                record.relative_index = (record.date_start - today_start).days
            elif record.bucket_id.bucket_type == "monthly":
                record.relative_index = (
                    record.date_start.year - today_start.year
                ) * 12 + (record.date_start.month - today_start.month)
            else:  # weekly
                record.relative_index = (record.date_start - today_start).days // 7

    @api.model
    def _search_relative_index(self, operator, value):
        bucket_type = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("project_task_planning.planning_bucket", "weekly")
        )
        today = fields.Date.context_today(self)
        today_start = self.env["project.bucket"]._get_bucket_start_date(
            today, bucket_type
        )
        if bucket_type == "daily":
            target_date_start = today_start + timedelta(days=value)
        elif bucket_type == "monthly":
            target_date_start = today_start + relativedelta(months=value)
        else:  # weekly
            target_date_start = today_start + timedelta(days=7 * value)
        return [
            ("date_start", operator, target_date_start),
            ("bucket_id.bucket_type", "=", bucket_type),
        ]

    working_hours = fields.Float(
        digits=(16, 2),
        compute="_compute_working_hours",
        store=True,
        help=(
            "Total working hours for the employee in this bucket after "
            "subtracting leaves."
        ),
    )

    planned_hours = fields.Float(
        digits=(16, 2),
        compute="_compute_planning_totals",
        store=True,
        help="Total planned hours for the employee in this bucket.",
    )

    remaining_hours = fields.Float(
        digits=(16, 2),
        compute="_compute_planning_totals",
        store=True,
        help="Remaining working capacity hours in this bucket.",
    )

    utilization_rate = fields.Float(
        digits=(16, 2),
        compute="_compute_utilization_rate",
        store=True,
        help="Percentage of working hours that are planned.",
    )

    planning_status = fields.Selection(
        [
            ("underplanned", "Underplanned"),
            ("optimal", "Optimal"),
            ("overplanned", "Overplanned"),
        ],
        compute="_compute_planning_status",
        store=True,
        help="Current planning load status of the employee based on the limits.",
    )

    task_planning_ids = fields.One2many(
        "project.task.planning",
        "employee_bucket_id",
        string="Planned Hours Details",
        readonly=True,
    )

    _employee_bucket_uniq = models.Constraint(
        "UNIQUE(employee_id, bucket_id)",
        "Theoretical capacity for an employee can only be defined once per bucket.",
    )

    @api.constrains("employee_id")
    def _check_employee_planning_enabled(self):
        for record in self:
            if record.employee_id.disable_planning:
                raise UserError(
                    self.env._(
                        "Cannot create or modify a capacity bucket for "
                        "employee '%s' because planning is disabled.",
                        record.employee_id.name,
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            plannings = self.env["project.task.planning"].search(
                [
                    ("employee_id", "=", record.employee_id.id),
                    ("bucket_id", "=", record.bucket_id.id),
                    ("employee_bucket_id", "=", False),
                ]
            )
            if plannings:
                plannings.write({"employee_bucket_id": record.id})
        return records

    def write(self, vals):
        res = super().write(vals)
        if "employee_id" in vals or "bucket_id" in vals:
            for record in self:
                plannings_new = self.env["project.task.planning"].search(
                    [
                        ("employee_id", "=", record.employee_id.id),
                        ("bucket_id", "=", record.bucket_id.id),
                    ]
                )
                plannings_old = self.env["project.task.planning"].search(
                    [
                        ("employee_bucket_id", "=", record.id),
                        "|",
                        ("employee_id", "!=", record.employee_id.id),
                        ("bucket_id", "!=", record.bucket_id.id),
                    ]
                )
                if plannings_new:
                    plannings_new.write({"employee_bucket_id": record.id})
                if plannings_old:
                    plannings_old.write({"employee_bucket_id": False})
        return res

    @api.depends("employee_id.resource_calendar_id", "date_start", "date_end")
    def _compute_working_hours(self):
        for record in self:
            record.working_hours = record._calculate_hours_for_period()

    @api.depends("task_planning_ids.planned_hours", "working_hours")
    def _compute_planning_totals(self):
        for record in self:
            total_planned = sum(
                planning.planned_hours for planning in record.task_planning_ids
            )
            record.planned_hours = total_planned
            record.remaining_hours = record.working_hours - total_planned

    @api.depends("planned_hours", "working_hours")
    def _compute_utilization_rate(self):
        for record in self:
            if record.working_hours:
                record.utilization_rate = (
                    record.planned_hours / record.working_hours
                ) * 100.0
            else:
                record.utilization_rate = 0.0

    @api.depends("utilization_rate")
    def _compute_planning_status(self):
        lower_limit_param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("project_task_planning.lower_planning_limit", "80.0")
        )
        upper_limit_param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("project_task_planning.upper_planning_limit", "100.0")
        )
        try:
            lower_limit = float(lower_limit_param)
        except ValueError:
            lower_limit = 80.0
        try:
            upper_limit = float(upper_limit_param)
        except ValueError:
            upper_limit = 100.0

        for record in self:
            if record.utilization_rate < lower_limit:
                record.planning_status = "underplanned"
            elif record.utilization_rate > upper_limit:
                record.planning_status = "overplanned"
            else:
                record.planning_status = "optimal"

    def _read_group(
        self,
        domain,
        groupby=(),
        aggregates=(),
        having=(),
        offset=0,
        limit=None,
        order=None,
    ):
        # Check if any requested aggregates are for utilization_rate
        utilization_rate_indices = []
        for i, spec in enumerate(aggregates):
            if spec.split(":")[0] == "utilization_rate":
                utilization_rate_indices.append(i)

        if not utilization_rate_indices:
            return super()._read_group(
                domain,
                groupby,
                aggregates,
                having=having,
                offset=offset,
                limit=limit,
                order=order,
            )

        # Ensure working_hours:sum and planned_hours:sum are in aggregates
        new_aggregates = list(aggregates)
        working_hours_in_query = any(
            spec.split(":")[0] == "working_hours" for spec in aggregates
        )
        planned_hours_in_query = any(
            spec.split(":")[0] == "planned_hours" for spec in aggregates
        )

        added_working = False
        added_planned = False

        if not working_hours_in_query:
            new_aggregates.append("working_hours:sum")
            added_working = True
        if not planned_hours_in_query:
            new_aggregates.append("planned_hours:sum")
            added_planned = True

        # Call super with the expanded aggregates
        res = super()._read_group(
            domain,
            groupby,
            tuple(new_aggregates),
            having=having,
            offset=offset,
            limit=limit,
            order=order,
        )

        groupby_len = len(groupby)

        # Find the index of working_hours and planned_hours in the queried aggregates
        working_idx = None
        planned_idx = None

        for i, spec in enumerate(new_aggregates):
            if spec.split(":")[0] == "working_hours":
                working_idx = groupby_len + i
            if spec.split(":")[0] == "planned_hours":
                planned_idx = groupby_len + i

        processed_res = []
        for row in res:
            row_list = list(row)

            working_sum = row_list[working_idx] if working_idx is not None else 0.0
            planned_sum = row_list[planned_idx] if planned_idx is not None else 0.0

            working_sum = working_sum or 0.0
            planned_sum = planned_sum or 0.0

            true_rate = (planned_sum / working_sum * 100.0) if working_sum else 0.0

            # Set utilization rate for all requested utilization_rate aggregates
            for u_idx in utilization_rate_indices:
                row_list[groupby_len + u_idx] = true_rate

            # Strip temporary DB aggregate fields from the end of the tuple
            if added_working or added_planned:
                strip_count = 0
                if added_working:
                    strip_count += 1
                if added_planned:
                    strip_count += 1
                row_list = row_list[:-strip_count]

            processed_res.append(tuple(row_list))

        return processed_res

    @api.model
    def _read_grouping_sets(self, domain, grouping_sets, aggregates=(), order=None):
        # Check if any requested aggregates are for utilization_rate
        utilization_rate_indices = []
        for i, spec in enumerate(aggregates):
            if spec.split(":")[0] == "utilization_rate":
                utilization_rate_indices.append(i)

        if not utilization_rate_indices:
            return super()._read_grouping_sets(
                domain, grouping_sets, aggregates, order=order
            )

        # Ensure working_hours:sum and planned_hours:sum are in aggregates
        new_aggregates = list(aggregates)
        working_hours_in_query = any(
            spec.split(":")[0] == "working_hours" for spec in aggregates
        )
        planned_hours_in_query = any(
            spec.split(":")[0] == "planned_hours" for spec in aggregates
        )

        added_working = False
        added_planned = False

        if not working_hours_in_query:
            new_aggregates.append("working_hours:sum")
            added_working = True
        if not planned_hours_in_query:
            new_aggregates.append("planned_hours:sum")
            added_planned = True

        # Call super with the expanded aggregates
        res = super()._read_grouping_sets(
            domain, grouping_sets, tuple(new_aggregates), order=order
        )

        # Process the results for each grouping set in grouping_sets
        processed_res = []
        for grouping_spec, group_results in zip(grouping_sets, res, strict=False):
            groupby_len = len(grouping_spec)

            # Find index of working_hours and planned_hours in aggregates
            working_idx = None
            planned_idx = None

            for i, spec in enumerate(new_aggregates):
                if spec.split(":")[0] == "working_hours":
                    working_idx = groupby_len + i
                if spec.split(":")[0] == "planned_hours":
                    planned_idx = groupby_len + i

            processed_group = []
            for row in group_results:
                row_list = list(row)

                working_sum = row_list[working_idx] if working_idx is not None else 0.0
                planned_sum = row_list[planned_idx] if planned_idx is not None else 0.0

                working_sum = working_sum or 0.0
                planned_sum = planned_sum or 0.0

                true_rate = (planned_sum / working_sum * 100.0) if working_sum else 0.0

                # Set utilization rate for all requested utilization_rate aggregates
                for u_idx in utilization_rate_indices:
                    row_list[groupby_len + u_idx] = true_rate

                # Strip temporary DB aggregate fields from the end of the tuple
                if added_working or added_planned:
                    strip_count = 0
                    if added_working:
                        strip_count += 1
                    if added_planned:
                        strip_count += 1
                    row_list = row_list[:-strip_count]

                processed_group.append(tuple(row_list))
            processed_res.append(processed_group)

        return processed_res

    def _calculate_hours_for_period(self):
        self.ensure_one()
        if not self.employee_id or not self.date_start or not self.date_end:
            return 0.0
        calendar = self.employee_id.resource_calendar_id
        if not calendar:
            return 0.0
        calendar_tz = calendar.tz or "UTC"

        # Convert start/end dates to datetime timezone-aware
        start_dt = fields.Datetime.context_timestamp(
            self.with_context(tz=calendar_tz),
            fields.Datetime.to_datetime(self.date_start),
        )
        end_dt = (
            fields.Datetime.context_timestamp(
                self.with_context(tz=calendar_tz),
                fields.Datetime.to_datetime(self.date_end),
            )
            + timedelta(days=1)
            - timedelta.resolution
        )

        work_hours = calendar.get_work_hours_count(start_dt, end_dt)
        leaves_hours = self._calculate_leave_hours(
            self.employee_id, start_dt, end_dt, calendar
        )
        return max(0.0, work_hours - leaves_hours)

    def _calculate_leave_hours(self, employee, start_dt, end_dt, calendar):
        if not employee or not calendar:
            return 0.0

        # Convert aware start_dt/end_dt to naive UTC datetimes for database query
        start_dt_naive = start_dt.astimezone(timezone.utc).replace(tzinfo=None)
        end_dt_naive = end_dt.astimezone(timezone.utc).replace(tzinfo=None)

        # Search for approved hr.leave records
        hr_leaves = self.env["hr.leave"].search(
            [
                ("employee_id", "=", employee.id),
                ("state", "=", "validate"),
                ("date_from", "<", end_dt_naive),
                ("date_to", ">", start_dt_naive),
            ]
        )

        # Search for employee resource-specific calendar leaves
        resource_leaves = []
        if employee.resource_id:
            resource_leaves = self.env["resource.calendar.leaves"].search(
                [
                    ("resource_id", "=", employee.resource_id.id),
                    ("date_from", "<", end_dt_naive),
                    ("date_to", ">", start_dt_naive),
                ]
            )

        # Collect intervals as (leave_start_dt, leave_end_dt) in calendar timezone
        intervals = []
        for leave in hr_leaves:
            l_start = fields.Datetime.context_timestamp(
                self.with_context(tz=calendar.tz), leave.date_from
            )
            l_end = fields.Datetime.context_timestamp(
                self.with_context(tz=calendar.tz), leave.date_to
            )
            intervals.append((max(l_start, start_dt), min(l_end, end_dt)))

        for leave in resource_leaves:
            l_start = fields.Datetime.context_timestamp(
                self.with_context(tz=calendar.tz), leave.date_from
            )
            l_end = fields.Datetime.context_timestamp(
                self.with_context(tz=calendar.tz), leave.date_to
            )
            intervals.append((max(l_start, start_dt), min(l_end, end_dt)))

        if not intervals:
            return 0.0

        # Sort and merge intervals to prevent double-counting
        intervals.sort(key=lambda x: x[0])
        merged_intervals = []
        for current in intervals:
            if current[0] >= current[1]:
                continue
            if not merged_intervals:
                merged_intervals.append(current)
            else:
                prev = merged_intervals[-1]
                if current[0] <= prev[1]:
                    merged_intervals[-1] = (prev[0], max(prev[1], current[1]))
                else:
                    merged_intervals.append(current)

        # Sum the work hours in each merged interval
        total_leave_hours = 0.0
        for l_start, l_end in merged_intervals:
            if l_start < l_end:
                total_leave_hours += calendar.get_work_hours_count(l_start, l_end)

        return total_leave_hours

    def _update_capacity_hours(self):
        for record in self:
            record.write({"working_hours": record._calculate_hours_for_period()})

    @api.model
    def cron_update_employee_capacity(self):
        # 1. Get months forward parameter
        months_forward_param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("project_task_planning.theoretical_capacity_months_forward", "6")
        )
        try:
            months_future = int(months_forward_param)
        except ValueError:
            months_future = 6

        # Calculate from N months past to N months future
        months_past_param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("project_task_planning.theoretical_capacity_months_past", "1")
        )
        try:
            months_past = int(months_past_param)
        except ValueError:
            months_past = 1
        today = fields.Date.today()

        # 2. Calculate date range boundaries
        date_from = today - relativedelta(months=months_past)
        date_to = today + relativedelta(months=months_future)

        # Find all employees with calendars
        employees = self.env["hr.employee"].search(
            [
                ("resource_calendar_id", "!=", False),
                ("disable_planning", "=", False),
            ]
        )

        # Generate buckets and capacities
        Bucket = self.env["project.bucket"]
        bucket_type = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("project_task_planning.planning_bucket", "weekly")
        )

        current_date = Bucket._get_bucket_start_date(date_from, bucket_type)
        end_boundary = Bucket._get_bucket_end_date(date_to, bucket_type)

        while current_date <= end_boundary:
            # 3. Get or create the master bucket record
            bucket_rec = Bucket._get_or_create_bucket(current_date)

            for emp in employees:
                # Find if capacity record already exists
                capacity_record = self.search(
                    [
                        ("employee_id", "=", emp.id),
                        ("bucket_id", "=", bucket_rec.id),
                    ],
                    limit=1,
                )

                # Calculate working hours
                calendar = emp.resource_calendar_id
                calendar_tz = calendar.tz or "UTC"
                start_dt = fields.Datetime.context_timestamp(
                    self.with_context(tz=calendar_tz),
                    fields.Datetime.to_datetime(bucket_rec.date_start),
                )
                end_dt = (
                    fields.Datetime.context_timestamp(
                        self.with_context(tz=calendar_tz),
                        fields.Datetime.to_datetime(bucket_rec.date_end),
                    )
                    + timedelta(days=1)
                    - timedelta.resolution
                )

                work_hours = calendar.get_work_hours_count(start_dt, end_dt)
                leaves_hours = self._calculate_leave_hours(
                    emp, start_dt, end_dt, calendar
                )
                working_hours = max(0.0, work_hours - leaves_hours)

                vals = {
                    "employee_id": emp.id,
                    "bucket_id": bucket_rec.id,
                    "working_hours": working_hours,
                }

                if capacity_record:
                    if abs(capacity_record.working_hours - working_hours) > 0.01:
                        capacity_record.write({"working_hours": working_hours})
                else:
                    self.create(vals)

            # Increment to next bucket
            if bucket_type == "daily":
                current_date += timedelta(days=1)
            elif bucket_type == "weekly":
                current_date += timedelta(weeks=1)
            elif bucket_type == "monthly":
                current_date = (
                    current_date.replace(day=28) + timedelta(days=4)
                ).replace(day=1)

        return True


class HRLeave(models.Model):
    _inherit = "hr.leave"

    def _get_affected_capacity_data(self):
        employee_ids = set()
        dates = []
        for leave in self:
            if leave.employee_id:
                employee_ids.add(leave.employee_id.id)
            if leave.date_from:
                dates.append(fields.Date.to_date(leave.date_from))
            if leave.date_to:
                dates.append(fields.Date.to_date(leave.date_to))
        if not employee_ids or not dates:
            return None
        return list(employee_ids), min(dates), max(dates)

    def _update_employee_capacity(self):
        data = self._get_affected_capacity_data()
        if data:
            employee_ids, min_date, max_date = data
            capacities = self.env["hr.employee.bucket"].search(
                [
                    ("employee_id", "in", employee_ids),
                    ("date_start", "<=", max_date),
                    ("date_end", ">=", min_date),
                ]
            )
            capacities._update_capacity_hours()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        validated_leaves = res.filtered(lambda leave: leave.state == "validate")
        if validated_leaves:
            validated_leaves._update_employee_capacity()
        return res

    def write(self, vals):
        pre_leaves = self.filtered(lambda leave: leave.state == "validate")
        pre_data = pre_leaves._get_affected_capacity_data() if pre_leaves else None

        res = super().write(vals)

        post_leaves = self.filtered(lambda leave: leave.state == "validate")
        post_data = post_leaves._get_affected_capacity_data() if post_leaves else None

        if pre_data:
            self.env["hr.employee.bucket"].search(
                [
                    ("employee_id", "in", pre_data[0]),
                    ("date_start", "<=", pre_data[2]),
                    ("date_end", ">=", pre_data[1]),
                ]
            )._update_capacity_hours()
        if post_data:
            self.env["hr.employee.bucket"].search(
                [
                    ("employee_id", "in", post_data[0]),
                    ("date_start", "<=", post_data[2]),
                    ("date_end", ">=", post_data[1]),
                ]
            )._update_capacity_hours()

        return res

    def unlink(self):
        validated_leaves = self.filtered(lambda leave: leave.state == "validate")
        data = (
            validated_leaves._get_affected_capacity_data() if validated_leaves else None
        )
        res = super().unlink()
        if data:
            self.env["hr.employee.bucket"].search(
                [
                    ("employee_id", "in", data[0]),
                    ("date_start", "<=", data[2]),
                    ("date_end", ">=", data[1]),
                ]
            )._update_capacity_hours()
        return res


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    def _get_affected_employees_and_dates(self):
        employee_ids = set()
        dates = []
        for leave in self:
            if leave.date_from:
                dates.append(fields.Date.to_date(leave.date_from))
            if leave.date_to:
                dates.append(fields.Date.to_date(leave.date_to))

            if leave.resource_id:
                emp = self.env["hr.employee"].search(
                    [("resource_id", "=", leave.resource_id.id)], limit=1
                )
                if emp:
                    employee_ids.add(emp.id)
            elif leave.calendar_id:
                emps = self.env["hr.employee"].search(
                    [("resource_calendar_id", "=", leave.calendar_id.id)]
                )
                employee_ids.update(emps.ids)
        if not employee_ids or not dates:
            return None
        return list(employee_ids), min(dates), max(dates)

    def _update_employee_capacity(self):
        data = self._get_affected_employees_and_dates()
        if data:
            employee_ids, min_date, max_date = data
            self.env["hr.employee.bucket"].search(
                [
                    ("employee_id", "in", employee_ids),
                    ("date_start", "<=", max_date),
                    ("date_end", ">=", min_date),
                ]
            )._update_capacity_hours()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._update_employee_capacity()
        return res

    def write(self, vals):
        pre_data = self._get_affected_employees_and_dates()
        res = super().write(vals)
        post_data = self._get_affected_employees_and_dates()

        if pre_data:
            self.env["hr.employee.bucket"].search(
                [
                    ("employee_id", "in", pre_data[0]),
                    ("date_start", "<=", pre_data[2]),
                    ("date_end", ">=", pre_data[1]),
                ]
            )._update_capacity_hours()
        if post_data:
            self.env["hr.employee.bucket"].search(
                [
                    ("employee_id", "in", post_data[0]),
                    ("date_start", "<=", post_data[2]),
                    ("date_end", ">=", post_data[1]),
                ]
            )._update_capacity_hours()
        return res

    def unlink(self):
        data = self._get_affected_employees_and_dates()
        res = super().unlink()
        if data:
            self.env["hr.employee.bucket"].search(
                [
                    ("employee_id", "in", data[0]),
                    ("date_start", "<=", data[2]),
                    ("date_end", ">=", data[1]),
                ]
            )._update_capacity_hours()
        return res
