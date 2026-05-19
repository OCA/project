# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProjectTags(models.Model):
    _inherit = "project.tags"

    company_id = fields.Many2one(comodel_name="res.company", string="Company")
