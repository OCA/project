# Copyright 2023 - Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    purchase_order_ids = fields.One2many(
        comodel_name="purchase.order",
        inverse_name="task_id",
        string="Purchase Orders",
        readonly=True,
    )
    purchase_order_count = fields.Integer(
        compute="_compute_purchase_order_count",
    )

    def action_create_purchase_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Purchase Order",
            "res_model": "purchase.order",
            "view_mode": "form",
            "context": {
                "default_task_id": self.id,
                "default_origin": self.name,
            },
        }

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "name": "Purchase Order",
            "res_model": "purchase.order",
            "context": {
                "default_task_id": self.id,
                "default_origin": self.name,
            },
        }
        if self.purchase_order_count == 1:
            action.update(
                {
                    "res_id": self.purchase_order_ids.id,
                    "view_mode": "form",
                }
            )
        else:
            action.update(
                {
                    "domain": [("id", "in", self.purchase_order_ids.ids)],
                    "view_mode": "tree,form",
                }
            )
        return action

    def _compute_purchase_order_count(self):
        for task in self:
            task.purchase_order_count = len(task.purchase_order_ids)
