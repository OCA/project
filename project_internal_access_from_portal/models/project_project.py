# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    privacy_visibility = fields.Selection(
        selection_add=[("portal_internal", "Invited internal/portal users")],
        ondelete={"portal_internal": "set default"},
    )
