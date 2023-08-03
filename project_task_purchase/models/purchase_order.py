# Copyright 2023 - Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    task_id = fields.Many2one(
        comodel_name="project.task",
        readonly=True,
    )

    def action_view_task(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Project Task",
            "res_model": "project.task",
            "view_mode": "form",
            "res_id": self.task_id.id,
        }
