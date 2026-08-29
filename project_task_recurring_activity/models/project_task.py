# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    recurring_activity_ids = fields.One2many(
        "recurring.activity", "project_task_id", string="activity", copy=True
    )
    custom_activity_ids = fields.Many2many(
        "recurring.activity",
        compute="_compute_activity_ids",
        store=True,
        copy=True,
    )

    @api.depends("recurring_activity_ids")
    def _compute_activity_ids(self):
        for item in self:
            item.custom_activity_ids = item.recurring_activity_ids.ids

    def call_create_recurring_tasks(self):
        for task in self.filtered(lambda t: t.recurrence_id):
            task.recurrence_id._create_next_occurrence(task)

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
                        "days_after_task_creation_date": (
                            item.days_after_task_creation_date
                        ),
                    },
                )
            )
        return result

    @api.model_create_multi
    def create(self, vals_list):
        results = super().create(vals_list)
        for item in results:
            if (
                item.recurring_task
                and item.custom_activity_ids
                and not self.env.context.get("copy_project")
            ):
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
        return results
