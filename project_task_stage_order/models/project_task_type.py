from odoo import api, fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    project_sequence_ids = fields.One2many(
        "project.task.type.sequence", "stage_id", string="Order per Project"
    )
    task_stage_order_enabled = fields.Boolean(
        compute="_compute_task_stage_order_enabled"
    )

    def _compute_task_stage_order_enabled(self):
        enabled = self.env.company.task_stage_order_enabled
        for stage in self:
            stage.task_stage_order_enabled = enabled

    def _is_order_feature_enabled(self):
        return self.env.company.task_stage_order_enabled

    def _sync_task_stage_order(self):
        if not self._is_order_feature_enabled():
            return
        Sequence = self.env["project.task.type.sequence"]
        for stage in self:
            linked_project_ids = Sequence.search(
                [("stage_id", "=", stage.id)]
            ).project_id.ids
            for project in stage.project_ids:
                if project.id not in linked_project_ids:
                    Sequence.create({
                        "project_id": project.id,
                        "stage_id": stage.id,
                        "sequence": stage.sequence,
                    })

    def _push_sequence_to_projects(self, new_sequence):
        Sequence = self.env["project.task.type.sequence"]
        for stage in self:
            rows = Sequence.search([("stage_id", "=", stage.id)])
            rows.write({"sequence": new_sequence})

    def write(self, vals):
        enabled = self._is_order_feature_enabled()
        project_id = self.env.context.get("default_project_id")
        redirected_sequence = None
        if enabled and "sequence" in vals and project_id and "project_ids" not in vals:
            redirected_sequence = vals.pop("sequence")
            Sequence = self.env["project.task.type.sequence"]
            for stage in self:
                row = Sequence.search(
                    [("stage_id", "=", stage.id), ("project_id", "=", project_id)],
                    limit=1,
                )
                if row:
                    row.sequence = redirected_sequence

        res = super().write(vals)

        if enabled:
            if "project_ids" in vals:
                self._sync_task_stage_order()
            if "sequence" in vals and redirected_sequence is None:
                self._push_sequence_to_projects(vals["sequence"])
        return res

    @api.model_create_multi
    def create(self, vals_list):
        enabled = self._is_order_feature_enabled()
        if enabled:
            for vals in vals_list:
                if "sequence" not in vals:
                    last = self.search(
                        [("user_id", "=", False)], order="sequence desc", limit=1
                    )
                    vals["sequence"] = last.sequence + 1 if last else 1
        stages = super().create(vals_list)
        if enabled:
            stages._sync_task_stage_order()
        return stages
