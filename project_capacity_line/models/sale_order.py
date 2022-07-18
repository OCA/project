# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    default_capacity_date_start = fields.Date()
    default_capacity_date_end = fields.Date()

    def action_cancel(self):
        res = super().action_cancel()
        self.filtered(lambda r: r.state == "cancel").mapped(
            "order_line"
        )._update_capacity_lines()
        return res

    def action_confirm(self):
        res = super().action_confirm()
        self.filtered(lambda r: r.state == "sale").mapped(
            "order_line"
        )._update_capacity_lines()
        return res

    def write(self, values):
        res = super().write(values)
        if self and "project_id" in values:
            self.env["capacity.line"].sudo().search(
                [("sale_id", "in", self.ids)]
            ).write({"project_id": values["project_id"]})
        return res
