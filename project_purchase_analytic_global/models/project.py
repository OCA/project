# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Project(models.Model):
    _inherit = "project.project"

    def action_open_project_purchase_orders(self):
        action_window = super().action_open_project_purchase_orders()
        context = action_window.setdefault("context", {})
        context["create"] = True
        if self.account_id:
            context["default_analytic_distribution"] = {str(self.account_id.id): 100.0}
        if action_window.get("res_id"):
            action_window["views"] = [[False, "list"], [False, "form"]]
            action_window["res_id"] = False
        return action_window
