# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from datetime import timedelta

from odoo import api, fields, models

WEEKS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "last": 4,
}


class ProjectTask(models.Model):
    _inherit = "project.task"

    recurring_activity_ids = fields.One2many(
        "recurring.activity", "project_task_id", string="activity", copy=True
    )
    custom_activity_ids = fields.Many2many(
        "recurring.activity", compute="_compute_activity_ids", store=True, copy=True
    )

    @api.depends("recurring_activity_ids")
    def _compute_activity_ids(self):
        for item in self:
            item.custom_activity_ids = item.recurring_activity_ids.ids

    @api.model
    def _get_recurring_fields(self):
        return ["custom_activity_ids"] + super()._get_recurring_fields()

    def call_create_recurring_tasks(self):
        self.recurrence_id.create_recurring_tasks()

    def _get_new_next_date_recurring_task(self):
        date = self.recurrence_id.next_recurrence_date
        delta = self.repeat_interval if self.repeat_unit == "day" else 1
        dates = self.recurrence_id._get_next_recurring_dates(
            date + timedelta(days=delta),
            self.repeat_interval,
            self.repeat_unit,
            self.repeat_type,
            self.repeat_until,
            self.repeat_on_month,
            self.repeat_on_year,
            self._get_weekdays(WEEKS.get(self.repeat_week)),
            self.repeat_day,
            self.repeat_week,
            self.repeat_month,
            count=1,
        )
        return dates[0]

    def _get_recurrence_start_date(self):
        if self.env.user.has_group("base.group_no_one"):
            return self.recurrence_id.next_recurrence_date or fields.Datetime.now()
        return super()._get_recurrence_start_date()

    @api.model
    def _forming_activity_data(self, task, custom_activity_ids):
        """Returns prepared data for creating records"""
        result = []
        for item in custom_activity_ids:
            result.append(
                (
                    0,
                    0,
                    {
                        "project_task_id": task.id,
                        "activity_type_id": item.activity_type_id.id,
                        "user_id": item.user_id.id,
                        "summary": item.summary,
                        "description": item.description,
                        "days_after_task_creation_date": item.days_after_task_creation_date,
                    },
                )
            )
        return result

    @api.model
    def create(self, val):
        result = super().create(val)
        for item in result:
            item.create_date = item.recurrence_id.next_recurrence_date
            if item.recurring_task and item.custom_activity_ids:
                item.message_subscribe(
                    partner_ids=list(
                        set(
                            item.custom_activity_ids.mapped("user_id")
                            .mapped("partner_id")
                            .ids
                        )
                        - set(item.message_follower_ids.mapped("partner_id").ids)
                    )
                )
                item.recurring_activity_ids = self._forming_activity_data(
                    item, item.custom_activity_ids
                )
        return result
