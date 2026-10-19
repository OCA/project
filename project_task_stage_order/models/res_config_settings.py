# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    task_stage_order_enabled = fields.Boolean(
        related="company_id.task_stage_order_enabled",
        readonly=False,
    )

    def set_values(self):
        result = super().set_values()
        if self.task_stage_order_enabled:
            self.env["project.task.type"].search([])._sync_task_stage_order()
        return result
