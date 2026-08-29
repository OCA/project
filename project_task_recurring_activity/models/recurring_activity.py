# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RecurringActivity(models.Model):
    _name = "recurring.activity"
    _description = "Recurring activity"

    project_task_id = fields.Many2one("project.task")
    activity_type_id = fields.Many2one(
        "mail.activity.type",
        string="Activity Type",
        ondelete="restrict",
    )
    user_id = fields.Many2one(
        "res.users",
        string="Assigned to",
        index=True,
        required=True,
        compute="_compute_on_activity_type_id",
        store=True,
        readonly=False,
    )
    summary = fields.Char(
        compute="_compute_on_activity_type_id",
        store=True,
        readonly=False,
    )
    description = fields.Html(
        sanitize_style=True,
        compute="_compute_on_activity_type_id",
        store=True,
        readonly=False,
    )
    days_after_task_creation_date = fields.Integer(
        string="Days after task creation",
        default=0,
        help="Number of days after task creation. 0 is treated as 1 day.",
    )
    next_recurrence_date = fields.Date(
        compute="_compute_next_recurrence_date",
        store=True,
    )

    @api.depends("days_after_task_creation_date")
    def _compute_next_recurrence_date(self):
        for record in self:
            record.next_recurrence_date = record._get_next_date()

    def _get_next_date(self):
        self.ensure_one()
        days = self.days_after_task_creation_date
        if days == 0:
            days = 1
        return fields.Date.today() + timedelta(days=days)

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
                date_deadline=today,
            )
            activity.write({"next_recurrence_date": activity._get_next_date()})

    @api.constrains("user_id")
    def _check_user_id(self):
        if self.env.context.get("skip_activity_user_check"):
            return
        if self.env.context.get("copy_project"):
            return
        for record in self:
            task = record.project_task_id
            if (
                record.user_id.partner_id.id
                not in task.message_follower_ids.mapped("partner_id").ids
            ):
                raise UserError(
                    _(
                        "Assigned user %s has no access to the document and is not "
                        "able to handle this activity."
                    )
                    % record.user_id.name
                )

    @api.depends("activity_type_id")
    def _compute_on_activity_type_id(self):
        for activity in self:
            if (not activity.description) or activity.description == "<p><br></p>":
                activity.description = activity.activity_type_id.default_note
            if not activity.summary:
                activity.summary = activity.activity_type_id.summary

    @api.model
    def delta_time(self, old, new):
        return (new - old).days

    @api.model_create_multi
    def create(self, vals_list):
        results = super().create(vals_list)
        for item in results:
            task = item.project_task_id
            task_base_date = (
                fields.Date.to_date(task.create_date) or fields.Date.today()
            )
            task.activity_schedule(
                activity_type_id=item.activity_type_id.id,
                user_id=item.user_id.id,
                note=item.description,
                summary=item.summary,
                date_deadline=task_base_date
                + timedelta(days=item.days_after_task_creation_date),
            )
        return results
