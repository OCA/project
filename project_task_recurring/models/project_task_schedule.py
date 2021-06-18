# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTaskSchedule(models.Model):

    _name = "project.task.schedule"
    _inherit = ["mail.thread", "recurrence.mixin"]
    _description = "Project Task Scheduling"
    _field_last_recurrency_date = "last_recurrency_date"
    _field_next_recurrency_date = "next_recurrency_date"

    name = fields.Char()
    project_id = fields.Many2one(comodel_name="project.project",)

    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("inactive", "Inactive")],
        default="draft",
    )

    # Recurrency
    recurrence_type = fields.Selection(
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)], "active": [("readonly", False)]},
    )
    last_recurrency_date = fields.Datetime()
    next_recurrency_date = fields.Datetime()

    # Task related fields
    task_template_id = fields.Many2one(
        comodel_name="project.task",
        domain=[("is_template_task", "=", True)],
        context={"default_is_template_task": True},
    )

    @api.model
    def _get_schedule_domain(self):
        return [("state", "=", "active")]

    def _get_task_default_values(self):
        return {"project_id": self.project_id.id}

    def _update_dates(self):
        self._set_next_recurrency_date()

    @api.model
    def _schedule_cron(self):
        schedules = self.search(self._get_schedule_domain())
        now = fields.Datetime.now()
        for schedule in schedules.filtered(
            lambda s: s.next_recurrency_date and s.next_recurrency_date < now
        ):
            default_values = schedule._get_task_default_values()
            schedule.task_template_id.copy(default_values)
            schedule._update_dates()
