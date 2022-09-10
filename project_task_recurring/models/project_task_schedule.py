# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


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
    last_recurrency_date = fields.Datetime(
        readonly=True,
        states={"draft": [("readonly", False)]},
        groups="project.group_project_manager",
        default=fields.Datetime.now(),
    )
    next_recurrency_date = fields.Datetime(readonly=True,)

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
        self._update_recurrency_date()

    def _create_dates(self):
        self._set_next_recurrency_date()

    def _create_tasks(self):
        """
            For all active schedules, and for those that have their next
            recurrency date before now, we create new task from the
            template ones.
        """
        now = fields.Datetime.now()
        for schedule in self.filtered(
            lambda s: s.state == "active"
            and s.next_recurrency_date
            and s.next_recurrency_date < now
        ):
            default_values = schedule._get_task_default_values()
            task = schedule.task_template_id.copy(default_values)
            schedule._update_dates()
            task.message_post(
                body=_("A new recurring task has been created!"),
                subtype_xmlid="project_task_recurring."
                "mail_message_subtype_recurring_task_created",
            )
            task.activity_schedule(
                "project_task_recurring.mail_act_new_recurring_task",
                task.date_deadline,
                user_id=task.user_id.id,
            )

    @api.model
    def _schedule_cron(self):
        """
            Get all schedules that are eligible to task generation
        """
        schedules = self.search(self._get_schedule_domain())
        schedules._create_tasks()

    def active(self):
        """
            Activate draft schedules
        """
        for schedule in self:
            if schedule.state != "active":
                schedule.write({"state": "active"})
                schedule._create_dates()
        return True

    def inactive(self):
        """
            Inactivate active schedules
        """
        self.filtered(lambda schedule: schedule.state == "active").write(
            {"state": "inactive"}
        )
        return True

    def draft(self):
        """
            Set in draft inactive schedules
        """
        self.filtered(lambda schedule: schedule.state == "inactive").write(
            {"state": "draft"}
        )
        return True
