# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class ProjectTask(models.Model):
    _inherit = "project.task"

    prioritizer_value = fields.Float(compute="_compute_prioritizer_value", store=True)
    prioritizer_line_ids = fields.Many2many("prioritizer.category.line")

    @api.depends("prioritizer_line_ids", "allocated_hours")
    def _compute_prioritizer_value(self):
        for rec in self:
            prioritizer_sum = sum([pcl.value for pcl in rec.prioritizer_line_ids])
            max_value = sum(
                [pc.max_value for pc in rec.project_id.prioritizer_category_ids]
            )
            locals_dict = {
                "prioritizer_sum": prioritizer_sum,
                "max_value": max_value,
                "allocated_hours": rec.allocated_hours,
                "rec": rec,
            }
            formula = rec.project_id.prioritizer_formula or "0"
            try:
                rec.prioritizer_value = safe_eval(formula, locals_dict=locals_dict)
            except Exception:
                rec.prioritizer_value = 0
