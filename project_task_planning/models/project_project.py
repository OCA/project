from odoo import api, fields, models


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


class ProjectProject(models.Model):
    _inherit = "project.project"

    total_estimated_hours_override = fields.Float(
        string="Total Estimated Target Hours",
        help=(
            "Set the target total estimated hours for this project. "
            "This will be used to scale and distribute hours to tasks."
        ),
        tracking=True,
    )

    pending_to_allocated_hours = fields.Float(
        string="Pending to Allocated Time",
        compute="_compute_pending_to_allocated_hours",
        store=True,
        readonly=True,
        help="Sum of pending to allocated hours from all tasks in the project.",
    )

    allocated_hours = fields.Float(
        string="Allocated Time",
        compute="_compute_allocated_hours",
        store=True,
        readonly=True,
        help="Sum of allocated hours from all tasks in the project.",
    )

    pending_to_plan_hours = fields.Float(
        string="Pending to Plan Hours",
        compute="_compute_pending_to_plan_hours",
        store=True,
        digits=(16, 2),
        help="Sum of pending to plan hours from all tasks in the project.",
    )

    total_planned_hours = fields.Float(
        compute="_compute_total_planned_hours",
        store=True,
        digits=(16, 2),
        help="Sum of planned hours from all tasks in the project.",
    )

    planning_total_display = fields.Char(
        compute="_compute_planning_displays",
    )

    planning_planned_display = fields.Char(
        compute="_compute_planning_displays",
    )

    planning_pct_display = fields.Char(
        string="Planning Percentage Display",
        compute="_compute_planning_displays",
    )

    @api.depends("task_ids.total_planned_hours")
    def _compute_total_planned_hours(self):
        for project in self:
            project.total_planned_hours = sum(
                task.total_planned_hours for task in project.task_ids
            )

    @api.depends("total_estimated_hours_override", "total_planned_hours")
    def _compute_planning_displays(self):
        for project in self:
            total_hours = project.total_estimated_hours_override or 0.0
            planned_hours = project.total_planned_hours or 0.0
            project.planning_total_display = _float_to_time_str(total_hours)
            project.planning_planned_display = _float_to_time_str(planned_hours)
            if total_hours > 0.0:
                pct = (planned_hours / total_hours) * 100.0
                project.planning_pct_display = f"{pct:.1f}%"
            else:
                project.planning_pct_display = "0.0%"

    @api.depends("task_ids.percentage_of_project_hours", "task_ids.allocated_hours")
    def _compute_pending_to_allocated_hours(self):
        for project in self:
            project.pending_to_allocated_hours = sum(
                max(task.percentage_of_project_hours - task.allocated_hours, 0.0)
                for task in project.task_ids
            )

    @api.depends("task_ids", "task_ids.allocated_hours")
    def _compute_allocated_hours(self):
        for project in self:
            project.allocated_hours = sum(
                task.allocated_hours for task in project.task_ids
            )

    @api.depends("task_ids", "task_ids.pending_to_plan_hours")
    def _compute_pending_to_plan_hours(self):
        for project in self:
            project.pending_to_plan_hours = sum(
                task.pending_to_plan_hours for task in project.task_ids
            )

    def action_view_planning(self):
        self.ensure_one()
        action = (
            self.sudo()
            .env.ref("project_task_planning.action_project_task_planning")
            .read()[0]
        )
        action["domain"] = [("project_id", "=", self.id)]
        action["context"] = {
            "default_project_id": self.id,
            "pivot_row_groupby": ["bucket"],
            "pivot_column_groupby": ["project_id", "task_id", "employee_id"],
            "pivot_measures": ["planned_hours"],
        }
        return action
