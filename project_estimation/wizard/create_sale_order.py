# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class ProjectEstimationCreateSaleOrder(models.TransientModel):
    _name = "project.estimation.create.sale.order"
    _description = "Create Sale Order from Estimation"

    estimation_id = fields.Many2one(
        comodel_name="project.estimation",
        required=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        related="estimation_id.partner_id",
    )
    line_ids = fields.One2many(
        comodel_name="project.estimation.create.sale.order.line",
        inverse_name="wizard_id",
        string="Sale Order Lines",
    )

    def _get_data_lines(self, line):
        return {
            "display_type": line.display_type,
            "product_id": line.product_id.id,
            "name": line.name,
            "product_uom_qty": line.product_uom_qty,
            "price_unit": line.price_unit,
            "tax_id": [Command.set(line.tax_id.ids)],
        }

    def _get_sale_order_vals(self):
        so_lines = [
            Command.create(self._get_data_lines(line)) for line in self.line_ids
        ]
        so_vals = [
            {
                "partner_id": self.partner_id.id,
                "origin": self.estimation_id.name,
                "project_estimation_id": self.estimation_id.id,
                "order_line": so_lines,
            }
        ]
        return so_vals

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        estimation_id = res.get("estimation_id") or self.env.context.get(
            "default_estimation_id"
        )
        if estimation_id:
            estimation = self.env["project.estimation"].browse(estimation_id)
            lines = [
                Command.create(self._get_data_lines(line))
                for line in estimation.line_ids
            ]
            res["line_ids"] = lines
        return res

    def action_create_sale_order(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(self.env._("No lines to create Sale Order."))

        # Create Sale Order
        so_vals = self._get_sale_order_vals()
        sale_order = self.env["sale.order"].create(so_vals)

        # Return action to view the created Sale Order
        return {
            "name": _("Sale Order"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "form",
            "res_id": sale_order.id,
        }


class ProjectEstimationCreateSaleOrderLine(models.TransientModel):
    _name = "project.estimation.create.sale.order.line"
    _description = "Create Sale Order Line"

    wizard_id = fields.Many2one(
        comodel_name="project.estimation.create.sale.order",
        required=True,
        ondelete="cascade",
    )
    display_type = fields.Selection(
        selection=[
            ("line_section", "Section"),
            ("line_note", "Note"),
        ],
        default=False,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
    )
    name = fields.Char(string="Description")
    product_uom_qty = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Float(string="Unit Price")
    tax_id = fields.Many2many(
        comodel_name="account.tax",
        string="Taxes",
    )
    price_subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_price_subtotal",
    )

    @api.depends("product_uom_qty", "price_unit")
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.price_unit
