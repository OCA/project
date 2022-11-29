from odoo import models


class Task(models.Model):
    _inherit = "project.task"

    def write(self, vals):
        result = super().write(vals)
        if (
            vals.get("stage_id")
            and self.env["project.task.type"].browse(vals.get("stage_id")).fold
        ):
            self._fold_personal_stage_task()
        return result

    def _fold_personal_stage_task(self):
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
        if not folded_stages:
            return
        # Allow to find personal stage with same name as shared stage
        stage_by_name = {stage.name: stage for stage in folded_stages}
        # Apply best matching personal stage
        for task in self:
            task.personal_stage_type_id = stage_by_name.get(
                task.stage_id.name,
                folded_stages[0],
            )
