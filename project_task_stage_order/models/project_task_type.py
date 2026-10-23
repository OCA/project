# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    project_sequence_ids = fields.One2many(
        "project.task.type.sequence", "stage_id", string="Order per Project"
    )

    def _is_order_feature_enabled(self):
        return self.env.company.task_stage_order_enabled

    def _sync_task_stage_order(self):
        if not self._is_order_feature_enabled():
            return
        Sequence = self.env["project.task.type.sequence"]
        for stage in self:
            existing_rows = Sequence.search([("stage_id", "=", stage.id)])
            linked_project_ids = stage.project_ids.ids
            values_to_create = [
                {
                    "project_id": project.id,
                    "stage_id": stage.id,
                    "sequence": stage.sequence,
                }
                for project in stage.project_ids
                if project.id not in existing_rows.project_id.ids
            ]
            if values_to_create:
                Sequence.create(values_to_create)
            rows_no_longer_linked = existing_rows.filtered(
                lambda row, linked=linked_project_ids: row.project_id.id not in linked
            )
            if rows_no_longer_linked:
                rows_no_longer_linked.unlink()

    def _push_sequence_to_projects(self, new_sequence):
        Sequence = self.env["project.task.type.sequence"]
        for stage in self:
            rows = Sequence.search([("stage_id", "=", stage.id)])
            rows.write({"sequence": new_sequence})

    @api.model
    def search_read(
        self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs
    ):
        result = super().search_read(
            domain=domain,
            fields=fields,
            offset=offset,
            limit=limit,
            order=order,
            **read_kwargs,
        )
        if order or limit or offset or not self._is_order_feature_enabled():
            return result
        project_id = None
        for leaf in domain or []:
            if (
                isinstance(leaf, list | tuple)
                and len(leaf) == 3
                and leaf[0] == "project_ids"
                and leaf[1] in ("=", "in")
            ):
                value = leaf[2]
                project_id = value[0] if isinstance(value, list | tuple) else value
                break
        if not project_id:
            return result
        ordered_stage_ids = (
            self.env["project.task.type.sequence"]
            .search(
                [
                    ("project_id", "=", project_id),
                    ("stage_id", "in", [row["id"] for row in result]),
                ]
            )
            .stage_id.ids
        )
        if not ordered_stage_ids:
            return result
        rank = {stage_id: index for index, stage_id in enumerate(ordered_stage_ids)}
        return sorted(
            result, key=lambda row: rank.get(row["id"], len(ordered_stage_ids))
        )

    def write(self, values):
        enabled = self._is_order_feature_enabled()
        project_id = self.env.context.get("default_project_id")
        redirected_sequence = None
        if (
            enabled
            and "sequence" in values
            and project_id
            and "project_ids" not in values
        ):
            values = dict(values)
            redirected_sequence = values.pop("sequence")
            Sequence = self.env["project.task.type.sequence"]
            for stage in self:
                row = Sequence.search(
                    [("stage_id", "=", stage.id), ("project_id", "=", project_id)],
                    limit=1,
                )
                if row:
                    row.sequence = redirected_sequence
        if enabled and "active" in values and not values["active"]:
            self.project_sequence_ids.with_context(force_delete=True).unlink()
        result = super().write(values)
        if enabled:
            if "project_ids" in values:
                self._sync_task_stage_order()
            if "sequence" in values and redirected_sequence is None:
                self._push_sequence_to_projects(values["sequence"])
            if "active" in values and values["active"]:
                self._sync_task_stage_order()
        return result

    @api.model_create_multi
    def create(self, values_list):
        enabled = self._is_order_feature_enabled()
        stages = super().create(values_list)
        if not enabled:
            return stages
        final_stages = self.env["project.task.type"]
        for stage in stages:
            existing_stage = self.env["project.task.type"]
            if stage.name and not stage.user_id:
                existing_stage = self.search(
                    [
                        ("name", "=", stage.name),
                        ("user_id", "=", False),
                        ("id", "!=", stage.id),
                    ],
                    limit=1,
                )
            if existing_stage:
                new_projects = stage.project_ids - existing_stage.project_ids
                if new_projects:
                    existing_stage.project_ids |= new_projects
                stage.unlink()
                final_stages |= existing_stage
            else:
                final_stages |= stage
        final_stages._sync_task_stage_order()
        return final_stages

    def unlink(self):
        project_id = self.env.context.get("default_project_id")
        if not project_id or not self._is_order_feature_enabled():
            return super().unlink()
        stages_to_fully_delete = self.env["project.task.type"]
        for stage in self:
            if project_id in stage.project_ids.ids and len(stage.project_ids) > 1:
                stage.project_ids = [(3, project_id)]
            else:
                stages_to_fully_delete |= stage
        task_count = self.env["project.task"].search_count(
            [("stage_id", "in", stages_to_fully_delete.ids)]
        )
        if task_count:
            stages_to_fully_delete.write({"active": False})
            stages_to_fully_delete = self.env["project.task.type"]
        return super(ProjectTaskType, stages_to_fully_delete).unlink()
