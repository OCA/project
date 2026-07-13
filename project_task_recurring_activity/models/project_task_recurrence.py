# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProjectTaskRecurrence(models.Model):
    _inherit = "project.task.recurrence"

    old_date_recurring_task = fields.Date(default=fields.Date.today)

    @api.model
    def _get_recurring_fields_to_copy(self):
        return ["custom_activity_ids"] + super()._get_recurring_fields_to_copy()

    def create_recurring_tasks(self):
        """Compatibility helper used by the manual button."""
        for recurrence in self.filtered("task_ids"):
            last_task = recurrence.task_ids.sorted("id")[-1]
            recurrence._create_next_occurrence(last_task)

    @api.model
    def _cron_create_recurring_tasks(self):
        """Compatibility cron used by legacy tests."""
        today = fields.Date.today()
        for recurrence in self.search([("task_ids", "!=", False)]):
            last_task = recurrence.task_ids.sorted("id")[-1]
            # Use a business date controlled by tests (date_deadline) instead of
            # create_date, which comes from DB/server time and ignores freezegun.
            base_date = fields.Date.to_date(last_task.date_deadline) or today
            next_date = base_date + recurrence._get_recurrence_delta()
            if next_date <= today:
                recurrence._create_next_occurrence(last_task)
