# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    project_costs_threshold = fields.Float(
        related="company_id.project_costs_threshold", readonly=False
    )

    @api.onchange("project_costs_threshold")
    def _reset_is_notfication_sent_cost_threshold(self):
        related_projects = self.env["project.project"].search(
            [
                ("costs_threshold", "=", False),
                ("is_notfication_sent_cost_threshold", "=", True),
            ]
        )
        related_projects.write({"is_notfication_sent_cost_threshold": False})
