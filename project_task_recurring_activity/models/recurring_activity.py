from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RecurringActivity(models.Model):
    _name = "recurring.activity"
    _description = "Recurring activity"

    project_task_id = fields.Many2one("project.task")
    activity_type_id = fields.Many2one(
        "mail.activity.type", string="Activity Type", ondelete="restrict"
    )
    user_id = fields.Many2one(
        "res.users",
        string="Assigned to",
        index=True,
        required=True,
    )
    summary = fields.Char(
        string="Summary",
    )
    description = fields.Html(
        string="Description",
        sanitize_style=True,
    )
    days_after_task_creation_date = fields.Integer()
    next_recurrence_date = fields.Date(
        string="next_date", compute="_compute_next_recurrence_date", store=True
    )

    @api.depends("days_after_task_creation_date")
    def _compute_next_recurrence_date(self):
        for record in self:
            record.next_recurrence_date = record._get_next_date()

    def _get_next_date(self):
        return fields.Date.today() + timedelta(
            days=self.days_after_task_creation_date + 1
            if self.days_after_task_creation_date == 0
            else self.days_after_task_creation_date
        )

    @api.model
    def _cron_create_activities(self):
        today = fields.Date.today()
        recurring_activities = self.search([("next_recurrence_date", "<=", today)])
        for activity in recurring_activities:
            activity.project_task_id.activity_schedule(
                activity_type_id=activity.activity_type_id.id,
                user_id=activity.user_id.id,
                note=activity.description,
                summary=activity.summary,
                date_deadline=fields.Date.today(),
            )
            activity.write({"next_recurrence_date": activity._get_next_date()})

    @api.constrains("user_id")
    def _check_user_id(self):
        for record in self:
            task = record.project_task_id
            if not (
                record.user_id.partner_id.id
                in task.message_follower_ids.mapped("partner_id").ids
            ):
                raise UserError(
                    _(
                        f"Assigned user {record.user_id.name} has no access"
                        " to the document and is not able to handle this activity."
                    )
                )

    @api.onchange("activity_type_id")
    def _onchange_activity_type_id(self):
        self.user_id = (
            self.user_id if self.user_id else self.activity_type_id.default_user_id
        )
        self.description = (
            self.activity_type_id.default_description
            if not self.description or self.description == "<p><br></p>"
            else self.description
        )
        self.summary = self.summary if self.summary else self.activity_type_id.summary

    @api.model
    def delta_time(self, old, new):
        return (new - old).days

    @api.model
    def create(self, val):
        result = super().create(val)
        for item in result:
            next_recurrence_date = (
                item.project_task_id.recurrence_id.next_recurrence_date
            )
            item.write({"create_date": next_recurrence_date})
            task = item.project_task_id
            old_date = item.project_task_id.recurrence_id.old_date_recurring_task
            delfa = 0
            if len(item.project_task_id.recurrence_id.task_ids) == 1:
                old_date = fields.Date.today()
                delfa = self.delta_time(old_date, next_recurrence_date)
            task.activity_schedule(
                activity_type_id=item.activity_type_id.id,
                user_id=item.user_id.id,
                note=item.description,
                summary=item.summary,
                date_deadline=fields.Date.today()
                + timedelta(days=item.days_after_task_creation_date)
                if not self.env.user.has_group("base.group_no_one")
                else (next_recurrence_date - timedelta(days=delfa))
                + timedelta(days=item.days_after_task_creation_date),
            )
        return result
