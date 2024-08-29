from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

DATE_OPTIONS = [
    ("1_weeks", _("1 Week")),
    ("2_weeks", _("2 Weeks")),
    ("1_months", _("1 Month")),
    ("2_months", _("2 Month")),
    ("1_years", _("1 Year")),
    ("2_years", _("2 Years")),
    ("custom", _("Custom")),
]


class ProjectSprint(models.Model):
    _name = "project.sprint"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Project Sprint"
    _sql_constraints = [
        (
            "date_check",
            "CHECK (date_start <= date_end)",
            _("Error: End date must be greater than start date!"),
        ),
    ]

    name = fields.Char(required=True, track_visibility="onchange")
    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Members",
        required=True,
        domain="[('share', '=', False), ('active', '=', True)]",
        track_visibility="onchange",
        relation="project_sprint_user_rel",
    )
    description = fields.Text(track_visibility="onchange")
    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        track_visibility="onchange",
        required=True,
    )
    task_ids = fields.One2many(
        comodel_name="project.task",
        inverse_name="sprint_id",
        string="Tasks",
        domain="[('project_id', '=', project_id)]",
    )
    date_start = fields.Date(
        string="Start Date", default=fields.Date.today, required=True
    )
    date_option = fields.Selection(
        selection=DATE_OPTIONS, default=DATE_OPTIONS[0][0], required=True
    )
    date_end = fields.Date(
        string="End Date",
        required=True,
        compute="_compute_date_end",
        store=True,
        readonly=False,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("done", "Done"),
        ],
        default="draft",
    )
    tasks_count = fields.Integer(compute="_compute_tasks_count")

    def _compute_tasks_count(self):
        for sprint in self:
            sprint.tasks_count = len(sprint.task_ids)

    def action_start(self):
        self.write({"state": "in_progress"})

    def action_done(self):
        self.write({"state": "done"})
        self._check_task_state()

    def action_tasks(self):
        self.ensure_one()
        return {
            "name": _("Tasks"),
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "view_mode": "tree,form",
            "domain": [("sprint_id", "=", self.id)],
            "context": {
                "default_project_id": self.project_id.id,
                "default_sprint_id": self.id,
            },
        }

    @api.model
    def cron_update_sprint_state(self):
        date = fields.Date.today()
        for sprint in self.search([("state", "=", "draft")]):
            if date >= sprint.date_start:
                sprint.write({"state": "in_progress"})

        for sprint in self.search([("state", "=", "in_progress")]):
            if date >= sprint.date_end:
                sprint.write({"state": "done"})
                sprint._check_task_state()

    def _check_task_state(self):
        self.ensure_one()
        in_progress_sprints = self.project_id.sprint_ids.filtered(
            lambda sprint: sprint.state == "in_progress"
        )
        self.task_ids.filtered(lambda task: task.kanban_state != "done").write(
            {
                "sprint_id": (
                    in_progress_sprints[0].id if in_progress_sprints else False
                ),
                "user_ids": False,
            }
        )

    @api.depends("date_start", "date_option")
    def _compute_date_end(self):
        for record in self:
            if record.date_option != "custom":
                num, interval = record.date_option.split("_")
                record.date_end = record.date_start + relativedelta(
                    **{interval: int(num)}
                )
            else:
                record.date_end = record.date_start + relativedelta(days=1)
