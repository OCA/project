# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .status_utils import NATIVE_STATUS_KEYS


class ProjectStateExtend(models.Model):
    _name = "project.state.extend"
    _description = "Extended Project State"
    _order = "sequence, name"

    name = fields.Char(
        required=True,
        translate=True,
    )
    technical_name = fields.Char(
        required=True,
        help="Technical name used internally. Must be unique and lowercase.",
    )
    color = fields.Integer(
        string="Color Index",
        required=True,
        default=0,
        help="Color index for the status bubble (0-11)",
    )
    sequence = fields.Integer(
        default=100,
        help="Sequence for ordering. Lower values appear first.",
    )
    active = fields.Boolean(
        default=True,
    )

    _sql_constraints = [
        (
            "technical_name_uniq",
            "unique(technical_name)",
            "Technical name must be unique!",
        )
    ]

    @api.constrains("technical_name")
    def _check_technical_name(self):
        pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        for record in self:
            technical_name = (record.technical_name or "").strip()
            if not pattern.match(technical_name):
                raise ValidationError(
                    _(
                        "Technical name must be lowercase, start with a letter, "
                        "and contain only letters, numbers, and underscores."
                    )
                )
            if technical_name in NATIVE_STATUS_KEYS:
                raise ValidationError(
                    _("Technical name '%s' is reserved by native project states.")
                    % technical_name
                )

    def unlink(self):
        for record in self:
            project_in_use = self.env["project.project"].search_count(
                [("last_update_status", "=", record.technical_name)]
            )
            update_in_use = self.env["project.update"].search_count(
                [("status", "=", record.technical_name)]
            )
            if project_in_use or update_in_use:
                raise ValidationError(
                    _(
                        "Cannot delete '%(name)s' because it is used in "
                        "%(projects)s project(s) and %(updates)s update(s)."
                    )
                    % {
                        "name": record.display_name,
                        "projects": project_in_use,
                        "updates": update_in_use,
                    }
                )
        return super().unlink()
