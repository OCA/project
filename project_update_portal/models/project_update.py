# Copyright 2025 Marcel Savegnago - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProjectUpdate(models.Model):
    _name = "project.update"
    _inherit = ["project.update", "portal.mixin"]

    @api.depends("project_id")
    def _compute_access_url(self):
        super()._compute_access_url()
        for update in self:
            if update.project_id:
                update.access_url = (
                    f"/my/projects/{update.project_id.id}/update/{update.id}"
                )
        return
