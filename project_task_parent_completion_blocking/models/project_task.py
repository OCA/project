from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.constrains("stage_id")
    def _check_subtasks_done_before_closing(self):
        for task in self:
            if task.stage_id.fold and task.child_ids.filtered(
                lambda t: not t.stage_id.fold
            ):
                raise ValidationError(
                    _("You can't close this task because it has open subtasks.")
                )
