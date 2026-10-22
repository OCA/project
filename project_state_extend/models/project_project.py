# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .status_utils import (
    NATIVE_PROJECT_STATUS_SELECTION,
    get_extended_status_color,
    get_extended_status_selection,
)


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.model
    def _get_extended_status_selection(self):
        return get_extended_status_selection(self.env, NATIVE_PROJECT_STATUS_SELECTION)

    # Override the last_update_status field to use dynamic selection
    last_update_status = fields.Selection(
        selection="_get_extended_status_selection",
        default="to_define",
        compute="_compute_last_update_status",
        store=True,
        readonly=False,
        required=True,
    )

    @api.depends("last_update_status")
    def _compute_last_update_color(self):
        extended_status_color = get_extended_status_color(self.env)
        for project in self:
            project.last_update_color = extended_status_color.get(
                project.last_update_status, 0
            )
