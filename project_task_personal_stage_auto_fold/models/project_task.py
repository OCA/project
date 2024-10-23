from odoo import models


class Task(models.Model):
    _inherit = "project.task"

    def write(self, vals):
        result = super().write(vals)
        stage_id = vals.get("stage_id")
        if stage_id and self.env["project.task.type"].browse(stage_id).fold:
            self._fold_personal_stage_task()
        return result

    def _fold_personal_stage_task(self):
        """
        Assigns a folded personal stage to tasks when they are moved to a folded stage.
        The function finds all folded stages associated with the current user and
        applies the best matching personal stage based on the task's stage name. If
        no exact match is found, the first available folded personal stage is assigned.
        """

        # Find all folded personal stages
        folded_stages = (
            self.env["project.task.type"]
            .search(
                [
                    ("user_id", "=", self.env.user.id),
                    ("fold", "=", True),
                ],
            )
            .sorted(lambda ptt: ptt.fold, reverse=True)
        )
        # Allow to find personal stage with same name as shared stage
        stage_by_name = {stage.name: stage for stage in folded_stages}
        # Apply best matching personal stage
        default_stage = folded_stages[0]
        for task in self:
            task.personal_stage_type_id = stage_by_name.get(
                task.stage_id.name,
                default_stage,
            )
