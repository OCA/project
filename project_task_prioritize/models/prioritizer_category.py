# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PrioritizerCategory(models.Model):
    _name = "prioritizer.category"
    _description = "Prioritizer Category"

    name = fields.Char()
    prioritizer_category_line_ids = fields.One2many(
        "prioritizer.category.line", inverse_name="prioritizer_category_id"
    )
    max_value = fields.Integer(compute="_compute_max_value", store=True)

    @api.depends("prioritizer_category_line_ids")
    def _compute_max_value(self):
        for rec in self:
            rec.max_value = (
                max([pcl.value for pcl in rec.prioritizer_category_line_ids])
                if rec.prioritizer_category_line_ids
                else 1
            )
