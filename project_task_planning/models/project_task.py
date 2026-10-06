from odoo import api, fields, models
from odoo.exceptions import UserError


def _float_to_time_str(value):
    if not value:
        return "00:00"
    negative = value < 0
    value = abs(value)
    hours = int(value)
    minutes = int(round((value - hours) * 60))
    if minutes == 60:
        hours += 1
        minutes = 0
    prefix = "-" if negative else ""
    return f"{prefix}{hours:02d}:{minutes:02d}"


class ProjectTask(models.Model):
    _inherit = "project.task"

    allocated_hours = fields.Float(
        string="Allocated Time",
        compute="_compute_allocated_hours",
        store=True,
        readonly=True,
        help="Sum of estimated hours from all technician allocations.",
    )

    percentage_of_project_hours = fields.Float(
        string="Estimated Hours",
        digits=(16, 2),
        help="Estimated hours for this task.",
    )

    pending_to_plan_hours = fields.Float(
        string="Pending to Plan Hours",
        compute="_compute_pending_to_plan_hours",
        store=True,
        digits=(16, 2),
        help="Calculated hours that are pending to be planned for this task.",
    )

    project_percentage = fields.Float(
        compute="_compute_project_percentage",
        store=True,
        digits=(16, 2),
        help="Percentage this task represents for the project.",
    )

    allocation_ids = fields.One2many(
        "project.task.allocation", "task_id", string="Technician Allocations"
    )

    total_planned_hours = fields.Float(
        compute="_compute_total_planned_hours",
        store=True,
        digits=(16, 2),
        help="Sum of planned hours from all technician allocations.",
    )

    planning_total_display = fields.Char(
        compute="_compute_planning_displays",
    )

    planning_planned_display = fields.Char(
        compute="_compute_planning_displays",
    )

    planning_pct_display = fields.Char(
        compute="_compute_planning_displays",
    )

    @api.depends("allocation_ids.total_planned_hours")
    def _compute_total_planned_hours(self):
        for task in self:
            task.total_planned_hours = sum(
                alloc.total_planned_hours for alloc in task.allocation_ids
            )

    @api.depends("percentage_of_project_hours", "total_planned_hours")
    def _compute_planning_displays(self):
        for task in self:
            total_hours = task.percentage_of_project_hours or 0.0
            planned_hours = task.total_planned_hours or 0.0
            task.planning_total_display = _float_to_time_str(total_hours)
            task.planning_planned_display = _float_to_time_str(planned_hours)
            if total_hours > 0.0:
                pct = (planned_hours / total_hours) * 100.0
                task.planning_pct_display = f"{pct:.1f}%"
            else:
                task.planning_pct_display = "0.0%"

    @api.depends(
        "stage_id",
        "stage_id.end",
        "percentage_of_project_hours",
        "allocation_ids.estimated_hours",
    )
    def _compute_pending_to_plan_hours(self):
        for task in self:
            if task.stage_id.end:
                task.pending_to_plan_hours = 0.0
            else:
                total_assigned_hours = sum(
                    task.allocation_ids.mapped("estimated_hours")
                )
                task.pending_to_plan_hours = max(
                    task.percentage_of_project_hours - total_assigned_hours, 0.0
                )

    @api.depends("allocation_ids.estimated_hours")
    def _compute_allocated_hours(self):
        for task in self:
            task.allocated_hours = sum(
                allocation.estimated_hours for allocation in task.allocation_ids
            )

    @api.depends(
        "percentage_of_project_hours",
        "project_id.total_estimated_hours_override",
    )
    def _compute_project_percentage(self):
        for task in self:
            total_hours = task.project_id.total_estimated_hours_override or 0.0
            if total_hours > 0.0:
                task.project_percentage = task.percentage_of_project_hours / total_hours
            else:
                task.project_percentage = 0.0

    def action_generate_allocation(self):
        employee_obj = self.env["hr.employee"]
        for record in self:
            if not record.user_ids:
                raise UserError(
                    self.env._(
                        "Cannot generate allocations: No users assigned to the task."
                    )
                )
            employees = employee_obj.search([("user_id", "in", record.user_ids.ids)])
            employee_qty = len(employees)
            if len(record.user_ids) != employee_qty:
                raise UserError(
                    self.env._(
                        "Cannot generate allocations: Some users assigned "
                        "to the task do not have linked employees."
                    )
                )

            disabled_employees = employees.filtered(lambda e: e.disable_planning)
            if disabled_employees:
                names = ", ".join(disabled_employees.mapped("name"))
                raise UserError(
                    self.env._(
                        "Cannot generate allocations: The following "
                        "assigned employees have planning disabled: %s",
                        names,
                    )
                )

            participation_percentage = 100.0 / employee_qty
            for employee in employees:
                record.env["project.task.allocation"].create(
                    {
                        "task_id": record.id,
                        "employee_id": employee.id,
                        "participation_percentage": participation_percentage,
                        "date_start": (
                            record.planned_date_start.date()
                            if record.planned_date_start
                            else False
                        ),
                        "date_end": (
                            record.planned_date_end.date()
                            if record.planned_date_end
                            else False
                        ),
                    }
                )

    def _validate_task_date(
        self, task_date, project_date, is_start_date, allocation_date_field
    ):
        if not task_date:
            return False

        messages = []
        date_type = "start" if is_start_date else "end"
        comparison = "earlier" if is_start_date else "later"

        # Validate against project date
        if project_date:
            task_date_value = (
                task_date.date() if hasattr(task_date, "date") else task_date
            )
            if (is_start_date and task_date_value < project_date) or (
                not is_start_date and task_date_value > project_date
            ):
                messages.append(
                    f"You are setting {date_type} date {comparison} than "
                    f"the project's planned {date_type} date: {project_date}"
                )

        # Validate against allocations
        task_date_value = task_date.date() if hasattr(task_date, "date") else task_date
        for allocation in self.allocation_ids:
            allocation_date = getattr(allocation, allocation_date_field)
            if not allocation_date:
                continue

            if (is_start_date and allocation_date < task_date_value) or (
                not is_start_date and allocation_date > task_date_value
            ):
                messages.append(
                    f"You are setting {date_type} date {comparison} than "
                    f"the task's planned {date_type} date. "
                    f"Employee {allocation.employee_id.name} - "
                    f"Allocation {date_type}s on {allocation_date}"
                )

        if messages:
            return {
                "warning": {
                    "title": f"{date_type.capitalize()} Date Warning",
                    "message": "\n".join(messages),
                    "type": "notification",
                }
            }
        return False

    @api.onchange("planned_date_start")
    def _onchange_planned_date_start(self):
        return self._validate_task_date(
            task_date=self.planned_date_start,
            project_date=self.project_id.date_start,
            is_start_date=True,
            allocation_date_field="date_start",
        )

    @api.onchange("planned_date_end")
    def _onchange_planned_date_end(self):
        return self._validate_task_date(
            task_date=self.planned_date_end,
            project_date=self.project_id.date,
            is_start_date=False,
            allocation_date_field="date_end",
        )

    def action_generate_planning(self):
        self.ensure_one()
        for allocation in self.allocation_ids:
            allocation.action_generate_planning()

    def action_view_planning(self):
        self.ensure_one()
        action = (
            self.sudo()
            .env.ref("project_task_planning.action_project_task_planning")
            .read()[0]
        )
        action["domain"] = [("task_id", "=", self.id)]
        action["context"] = {
            "default_task_id": self.id,
            "default_project_id": self.project_id.id,
            "pivot_row_groupby": ["bucket"],
            "pivot_column_groupby": ["project_id", "task_id", "employee_id"],
            "pivot_measures": ["planned_hours"],
        }
        return action

    @api.constrains("allocation_ids")
    def _check_allocation_hours_consistency(self):
        for task in self:
            if sum(task.allocation_ids.mapped("participation_percentage")) > 100.0:
                raise UserError(
                    self.env._(
                        "The sum of allocation percentage on task '%s' "
                        "can't be greater than 100%%.",
                        task.name,
                    )
                )

    @api.constrains("percentage_of_project_hours", "project_percentage")
    def _check_project_percentage(self):
        for task in self:
            if task.percentage_of_project_hours < 0.0:
                raise UserError(
                    self.env._(
                        "The estimated hours for task '%s' cannot be negative.",
                        task.name,
                    )
                )
            total_project_percentage = sum(
                task.project_id.task_ids.mapped("project_percentage")
            )
            if total_project_percentage > 1.0001:
                raise UserError(
                    self.env._(
                        "The sum of estimated hours for all tasks in the "
                        "project cannot exceed the project target estimated "
                        "hours."
                    )
                )


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    end = fields.Boolean(string="End Status", default=False)
