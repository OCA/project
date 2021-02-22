# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class SaleOrder(models.Model):
    """
    Set tracking items with planned hours
    - on confirm
    - on add line or edit quantity on confirmed SO lines
    """

    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        self.mapped("order_line").set_tracking_item(update_planned=True)
        return res


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line"]

    def _get_tracking_planned_qty(self):
        super()._get_tracking_planned_qty()
        return self.product_uom_qty

    def _prepare_tracking_item_values(self):
        vals = super()._prepare_tracking_item_values()
        analytic = self.order_id.analytic_account_id
        if analytic:
            vals.update(
                {
                    "analytic_id": analytic.id,
                    "product_id": self.product_id.id,
                    "sale_order_line_id": self.id,
                }
            )
        return vals

    def _get_tracking_items(self):
        """
        Lines ellegible to be tracked:
        - SO is Confirmed
        - SO has an Analytic Account
        - Product is type service
        """
        return (
            self.filtered(lambda l: l.order_id.state == "sale")
            .filtered("order_id.analytic_account_id")
            .filtered(lambda l: l.product_id.type == "service")
        )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.set_tracking_item(update_planned=True)
        return res

    def write(self, vals):
        res = super().write(vals)
        if "product_uom_qty" in vals or "price_unit" in vals:
            self.set_tracking_item(update_planned=True)
        return res
