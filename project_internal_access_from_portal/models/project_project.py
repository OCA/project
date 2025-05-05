# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Adding a new selection option to the privacy_visibility field
    privacy_visibility = fields.Selection(
        selection_add=[('portal_internal', 'Invited internal/portal users')],
        ondelete={'portal_internal': 'set default'},
        help="Show this project to invited internal users and portal users",
    )
