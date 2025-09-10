# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PrioritizerCategoryLine(models.Model):
    _name = "prioritizer.category.line"
    _description = "Prioritizer Category Line"

    name = fields.Char()
    value = fields.Integer()
    prioritizer_category_id = fields.Many2one(comodel_name="prioritizer.category")
