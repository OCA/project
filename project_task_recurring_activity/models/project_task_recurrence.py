from odoo import api, fields, models


class ProjectTaskRecurrence(models.Model):
    _inherit = "project.task.recurrence"

    old_date_recurring_task = fields.Date(
        default=fields.Date.today(),
    )

    @api.model
    def _get_recurring_fields(self):
        return ["custom_activity_ids"] + super()._get_recurring_fields()

    def create_recurring_tasks(self):
        """Create recurring tasks"""
        if not self.env.user.has_group("project.group_project_recurring_tasks"):
            return
        self._create_next_task()
        for recurrence in self.filtered(lambda r: r.repeat_type == "after"):
            recurrence.recurrence_left -= 1
        task = self.task_ids[-1]
        new_date = task._get_new_next_date_recurring_task()

        self.write(
            {
                "old_date_recurring_task": self.next_recurrence_date,
                "next_recurrence_date": new_date,
            }
        )
        task.write({"create_date": new_date})
