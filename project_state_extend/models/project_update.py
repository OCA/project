# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .status_utils import (
    NATIVE_UPDATE_STATUS_SELECTION,
    get_extended_status_color,
    get_extended_status_selection,
)


class ProjectUpdate(models.Model):
    _inherit = "project.update"

    @api.model
    def _get_extended_status_selection(self):
        return get_extended_status_selection(self.env, NATIVE_UPDATE_STATUS_SELECTION)

    # Override the status field to use dynamic selection
    status = fields.Selection(
        selection="_get_extended_status_selection",
        required=True,
        tracking=True,
    )

    @api.depends("status")
    def _compute_color(self):
        extended_status_color = get_extended_status_color(self.env)
        for update in self:
            update.color = extended_status_color.get(update.status, 0)
