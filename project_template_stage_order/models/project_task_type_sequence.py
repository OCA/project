# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, models
from odoo.exceptions import UserError


class ProjectTaskTypeSequence(models.Model):
    _inherit = "project.task.type.sequence"

    def write(self, values):
        if (
            "sequence" not in values
            or self.env.context.get("template_propagate")
            or not self.env.company.task_stage_order_enabled
        ):
            return super().write(values)
        for row in self:
            if row.project_id.template_id:
                raise UserError(
                    _(
                        'You cannot reorder stages on "%(project)s" because '
                        'it follows the template "%(template)s". Change the '
                        "order on the template instead.",
                        project=row.project_id.name,
                        template=row.project_id.template_id.name,
                    )
                )
        result = super().write(values)
        for row in self:
            children = row.project_id.template_child_ids
            if not children:
                continue
            child_rows = self.search(
                [
                    ("stage_id", "=", row.stage_id.id),
                    ("project_id", "in", children.ids),
                ]
            )
            if child_rows:
                child_rows.with_context(template_propagate=True).write(
                    {"sequence": values["sequence"]}
                )
        return result
