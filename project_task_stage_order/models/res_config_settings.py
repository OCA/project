from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    task_stage_order_enabled = fields.Boolean(
        related="company_id.task_stage_order_enabled",
        string="Per-Project Task Stage Order",
        readonly=False,
    )

    def set_values(self):
        super().set_values()
        if self.task_stage_order_enabled:
            self.env["project.task.type"].search([])._sync_task_stage_order()
