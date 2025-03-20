# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class Projectproject(models.Model):
    _inherit = "project.project"

    tag_ids = fields.Many2many(
        domain="""['|', ('allowed_project_ids', 'in', [id]),
        ('allowed_project_ids', '=', False)]"""
    )
