from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProjectTaskAllocation(models.Model):
    _name = "project.task.allocation"
    _description = "Project Task Allocation"
    _order = "task_id, employee_id"

    task_id = fields.Many2one(
        "project.task", string="Task", required=True, ondelete="cascade"
    )
    project_id = fields.Many2one(
        related="task_id.project_id", string="Project", store=True, readonly=True
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        domain=[("disable_planning", "=", False)],
    )

    participation_percentage = fields.Float(
        string="Participation (%)",
        digits=(16, 2),
        default=100.0,
        help="Percentage of this task's effort assigned to this employee.",
    )
    block_participation_percentage = fields.Boolean(
        string="Block Participation %",
        default=False,
        compute="_compute_block_participation_percentage",
        store=True,
        help="If checked, the participation percentage cannot be modified.",
    )
    estimated_hours = fields.Float(
        string="Assigned Hours",
        compute="_compute_estimated_hours",
        inverse="_inverse_estimated_hours",
        store=True,
        readonly=False,
        help=(
            "Estimated hours for this employee on this task. Calculated from "
            "task percentage of project hours and participation %, can be "
            "adjusted."
        ),
    )

    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")

    planning_ids = fields.One2many(
        "project.task.planning",
        "allocation_id",
        string="Planning",
    )

    total_planned_hours = fields.Float(
        compute="_compute_planning_totals",
        store=True,
        digits=(16, 2),
        help="Sum of planned hours from all planning entries.",
    )

    pending_to_plan_hours = fields.Float(
        string="Pending to Plan Hours",
        compute="_compute_pending_to_plan_hours",
        store=True,
        digits=(16, 2),
        help="Calculated hours that are pending to be planned for this allocation.",
    )

    @api.onchange("date_start")
    def _onchange_date_start(self):
        if (
            self.date_start
            and self.task_id.planned_date_start
            and self.date_start < self.task_id.planned_date_start.date()
        ):
            return {
                "warning": {
                    "title": "Previous Date Warning",
                    "message": (
                        "You are setting a start date earlier than the "
                        "task's planned start date."
                    ),
                    "type": "notification",
                }
            }

    @api.onchange("date_end")
    def _onchange_date_end(self):
        if (
            self.date_end
            and self.task_id.planned_date_end
            and self.date_end > self.task_id.planned_date_end.date()
        ):
            return {
                "warning": {
                    "title": "Later Date Warning",
                    "message": (
                        "You are setting an end date later than the "
                        "task's planned end date."
                    ),
                    "type": "notification",
                }
            }

    @api.depends("planning_ids", "planning_ids.blocked")
    def _compute_block_participation_percentage(self):
        for allocation in self:
            allocation.block_participation_percentage = bool(
                allocation.planning_ids.filtered(lambda p: p.blocked)
            )

    @api.depends("estimated_hours", "total_planned_hours")
    def _compute_pending_to_plan_hours(self):
        for allocation in self:
            allocation.pending_to_plan_hours = (
                allocation.estimated_hours - allocation.total_planned_hours
            )

    @api.depends("planning_ids", "planning_ids.planned_hours")
    def _compute_planning_totals(self):
        for allocation in self:
            allocation.total_planned_hours = sum(
                planning.planned_hours for planning in allocation.planning_ids
            )

    @api.depends("task_id.percentage_of_project_hours", "participation_percentage")
    def _compute_estimated_hours(self):
        for allocation in self:
            if (
                allocation.task_id
                and allocation.task_id.percentage_of_project_hours
                and allocation.task_id.percentage_of_project_hours > 0
            ):
                allocation.estimated_hours = (
                    allocation.participation_percentage
                    * allocation.task_id.percentage_of_project_hours
                    / 100.0
                )
            else:
                allocation.estimated_hours = 0.0

    def _inverse_estimated_hours(self):
        for allocation in self:
            if (
                allocation.task_id
                and allocation.task_id.percentage_of_project_hours
                and allocation.task_id.percentage_of_project_hours > 0
            ):
                allocation.participation_percentage = (
                    allocation.estimated_hours
                    / allocation.task_id.percentage_of_project_hours
                    * 100.0
                )
            else:
                allocation.participation_percentage = 0.0

    def action_generate_planning(self):
        Planning = self.env["project.task.planning"]

        for allocation in self:
            if (
                not allocation.date_start
                or not allocation.date_end
                or not allocation.estimated_hours > 0
            ):
                continue

            # Remove unblocked planning entries to avoid duplicates
            existing_plannings = allocation.planning_ids.filtered(
                lambda p: not p.blocked
            )
            existing_plannings.unlink()

            # Determine available start and end dates
            blocked_plannings = allocation.planning_ids.filtered(lambda p: p.blocked)
            date_start = (
                blocked_plannings
                and max(
                    allocation.date_start,
                    max(p.date_end for p in blocked_plannings) + timedelta(days=1),
                )
                or allocation.date_start
            )
            date_end = allocation.date_end

            # Calculate remaining hours to plan
            blocked_hours = sum(blocked_plannings.mapped("planned_hours"))
            hours_to_plan = max(allocation.estimated_hours - blocked_hours, 0.0)

            # Calculate total days in the remaining allocation period
            current_date = fields.Date.from_string(date_start)
            end_date = fields.Date.from_string(date_end)
            total_days_in_period = (end_date - current_date).days + 1

            if total_days_in_period <= 0 or hours_to_plan <= 0:
                continue

            # Calculate hours per day (simple distribution)
            hours_per_day = hours_to_plan / total_days_in_period

            # Group daily hours by bucket
            bucket_data = {}
            for i in range(total_days_in_period):
                day = current_date + timedelta(days=i)
                bucket_rec = self.env["project.bucket"]._get_or_create_bucket(day)
                if bucket_rec.id not in bucket_data:
                    bucket_data[bucket_rec.id] = {
                        "hours": 0.0,
                    }
                bucket_data[bucket_rec.id]["hours"] += hours_per_day

            # Create or update planning records
            for bucket_id_val in sorted(bucket_data.keys()):
                data = bucket_data[bucket_id_val]
                planned_hours_for_bucket = data["hours"]

                planning_for_bucket = Planning.search(
                    [
                        ("allocation_id", "=", allocation.id),
                        ("bucket_id", "=", bucket_id_val),
                    ],
                    limit=1,
                )
                if planning_for_bucket:
                    planning_for_bucket.write(
                        {"planned_hours": planned_hours_for_bucket}
                    )
                else:
                    Planning.create(
                        {
                            "allocation_id": allocation.id,
                            "bucket_id": bucket_id_val,
                            "planned_hours": planned_hours_for_bucket,
                        }
                    )
        return True

    @api.constrains("participation_percentage")
    def _check_participation_percentage(self):
        for allocation in self:
            if allocation.participation_percentage < 0.0:
                raise UserError(
                    self.env._(
                        "The allocation percentage for employee '%s' "
                        "cannot be negative.",
                        allocation.employee_id.name,
                    )
                )

    @api.constrains("employee_id")
    def _check_employee_planning_enabled(self):
        for allocation in self:
            if allocation.employee_id.disable_planning:
                raise UserError(
                    self.env._(
                        "The employee '%s' has planning disabled and "
                        "cannot be allocated.",
                        allocation.employee_id.name,
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_task_dates()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "date_start" in vals or "date_end" in vals:
            self._sync_task_dates()
        return res

    def _sync_task_dates(self):
        tasks = self.mapped("task_id")
        for task in tasks:
            allocs = task.allocation_ids
            start_dates = [a.date_start for a in allocs if a.date_start]
            end_dates = [a.date_end for a in allocs if a.date_end]

            task_vals = {}
            if start_dates:
                task_vals["planned_date_start"] = min(start_dates)
            if end_dates:
                task_vals["planned_date_end"] = max(end_dates)

            if task_vals:
                task.write(task_vals)

    def _sync_allocation_dates_from_alloc(self):
        for alloc in self:
            plannings = alloc.planning_ids.filtered(lambda p: p.planned_hours > 0.0)
            if plannings:
                start_dates = [p.date_start for p in plannings if p.date_start]
                end_dates = [p.date_end for p in plannings if p.date_end]

                alloc_vals = {}
                if start_dates:
                    alloc_vals["date_start"] = min(start_dates)
                if end_dates:
                    alloc_vals["date_end"] = max(end_dates)

                if alloc_vals:
                    alloc.write(alloc_vals)
