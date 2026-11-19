# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectSharingCollaboratorWizard(models.TransientModel):
    _inherit = "project.share.collaborator.wizard"

    readonly = fields.Boolean(default=False)
