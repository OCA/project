# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import api, fields, models


class ProjectTaskMaterial(models.Model):
    _inherit = "project.task.material"

    cost = fields.Float(
        compute="_compute_purchase_price",
        min_display_digits="Product Price",
        store=True,
        readonly=False,
        copy=False,
        precompute=True,
        groups="base.group_user",
    )

    @api.depends("product_id")
    def _compute_purchase_price(self):
        for line in self:
            line.cost = line.product_id.standard_price or 0.0
