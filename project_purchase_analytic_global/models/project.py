# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Project(models.Model):
    _inherit = "project.project"

    def action_open_project_purchase_orders(self):
        action_window = super().action_open_project_purchase_orders()
        purchase_orders = self.env["purchase.order"].search(action_window["domain"])
        action_window.update(
            {
                "context": {
                    "create": True,
                    "default_analytic_distribution": {self.account_id.id: 100.0},
                }
            }
        )
        if len(purchase_orders) == 1:
            action_window.update({"views": [[False, "tree"], [False, "form"]]})
            action_window.update({"res_id": None})
        return action_window
