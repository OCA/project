# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProjectTaskTypeSequence(models.Model):
    _name = "project.task.type.sequence"
    _description = "Task Stage order per Project"
    _order = "sequence"

    project_id = fields.Many2one("project.project", required=True, ondelete="cascade")
    stage_id = fields.Many2one("project.task.type", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        "res.company",
        related="project_id.company_id",
        store=True,
        index=True,
    )

    @api.model_create_multi
    def create(self, values_list):
        rows = super().create(values_list)
        for row in rows:
            if row.project_id not in row.stage_id.project_ids:
                row.stage_id.project_ids += row.project_id
        return rows

    def unlink(self):
        project_ids = self.mapped("project_id").ids
        stage_ids = self.mapped("stage_id").ids
        task_counts = self.env["project.task"]._read_group(
            [("project_id", "in", project_ids), ("stage_id", "in", stage_ids)],
            ["project_id", "stage_id"],
            ["__count"],
        )
        counts_by_pair = {
            (project.id, stage.id): count for project, stage, count in task_counts
        }
        for row in self:
            count = counts_by_pair.get((row.project_id.id, row.stage_id.id), 0)
            if count:
                raise UserError(
                    _(
                        'You cannot remove stage "%(stage)s" from project '
                        '"%(project)s" because it still has %(count)s task(s). '
                        "Please move or delete those tasks first.",
                        stage=row.stage_id.name,
                        project=row.project_id.name,
                        count=count,
                    )
                )

        projects_by_stage = {}
        for row in self:
            projects_by_stage.setdefault(row.stage_id, self.env["project.project"])
            projects_by_stage[row.stage_id] |= row.project_id

        result = super().unlink()

        stages_left_empty = self.env["project.task.type"]
        for stage, projects in projects_by_stage.items():
            stage.project_ids -= projects
            if not stage.project_ids:
                stages_left_empty |= stage

        if stages_left_empty:
            stages_left_empty.unlink()
        return result
