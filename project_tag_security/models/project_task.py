# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    tag_ids = fields.Many2many(
        domain="""['|', ('allowed_project_ids', 'in', [project_id]),
        ('allowed_project_ids', '=', False)]"""
    )
