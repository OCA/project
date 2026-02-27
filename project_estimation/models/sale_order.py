# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    project_estimation_id = fields.Many2one(
        comodel_name="project.estimation",
    )

    def action_view_estimation(self):
        self.ensure_one()
        return {
            "name": self.env._("Project Estimation"),
            "type": "ir.actions.act_window",
            "res_model": "project.estimation",
            "view_mode": "form",
            "res_id": self.project_estimation_id.id,
        }
