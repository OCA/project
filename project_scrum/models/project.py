from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = "project.project"

    sprint_ids = fields.One2many(
        comodel_name="project.sprint",
        inverse_name="project_id",
        string="Sprints",
    )
    sprint_count = fields.Integer(compute="_compute_sprint_count")
    backlog_count = fields.Integer(compute="_compute_backlog_count")

    def _compute_backlog_count(self):
        for project in self:
            project.backlog_count = len(
                project.task_ids.filtered(
                    lambda task: not task.sprint_id and task.kanban_state != "done"
                )
            )

    def _compute_sprint_count(self):
        for project in self:
            project.sprint_count = len(project.sprint_ids)

    def action_sprints(self):
        self.ensure_one()
        return {
            "name": _("Sprints"),
            "type": "ir.actions.act_window",
            "res_model": "project.sprint",
            "view_mode": "tree,form,timeline",
            "domain": [("project_id", "=", self.id)],
            "context": {"default_project_id": self.id},
        }

    def action_backlog(self):
        self.ensure_one()
        return {
            "name": _("Backlog"),
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "view_mode": "tree,form",
            "domain": [
                ("project_id", "=", self.id),
                ("sprint_id", "=", False),
                ("kanban_state", "!=", "done"),
            ],
            "context": {"default_project_id": self.id},
        }

    def action_sprint_timeline(self):
        self.ensure_one()
        return {
            "name": _("Sprint Timeline"),
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "view_mode": "timeline",
            "domain": [("project_id", "=", self.id), ("sprint_id", "!=", False)],
            "context": {"default_project_id": self.id, "no_create": True},
        }


class ProjectTask(models.Model):
    _inherit = "project.task"

    sprint_id = fields.Many2one(
        comodel_name="project.sprint",
        string="Sprint",
        track_visibility="onchange",
    )

    sprint_state = fields.Selection(
        related="sprint_id.state", string="Sprint State", store=True
    )

    @api.constrains("user_ids")
    def _check_user_ids(self):
        for task in self:
            if task.user_ids and task.sprint_id:
                if not task.user_ids <= task.sprint_id.user_ids:
                    raise ValidationError(
                        _("The assignees must be part of the sprint.")
                    )

    @api.onchange("sprint_id")
    def _onchange_sprint_id(self):
        self.user_ids = False
