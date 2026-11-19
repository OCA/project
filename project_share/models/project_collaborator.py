# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectCollaborator(models.Model):
    _inherit = "project.collaborator"

    readonly = fields.Boolean(default=False)
