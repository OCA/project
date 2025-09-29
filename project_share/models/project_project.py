# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    edit_collaborator_ids = fields.One2many(
        "project.collaborator",
        "project_id",
        string="Collaborators",
        copy=False,
        domain=[("readonly", "=", False)],
    )

    def _check_project_sharing_access(self, check_readonly=False):
        result = super()._check_project_sharing_access()
        if (
            check_readonly
            and isinstance(result, models.BaseModel)
            and result._name == "project.collaborator"
        ):
            return result.filtered(lambda c: not c.readonly)
        return result
