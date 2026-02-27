# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectEstimationLine(models.Model):
    _name = "project.estimation.line"
    _description = "Project Estimation Line"
    _order = "sequence, id"

    estimation_id = fields.Many2one(
        comodel_name="project.estimation",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    display_type = fields.Selection(
        selection=[
            ("line_section", "Section"),
            ("line_note", "Note"),
        ],
        default=False,
    )
    name = fields.Char(
        string="Description",
        compute="_compute_name",
        store=True,
        readonly=False,
        required=True,
        precompute=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
    )
    cost_type = fields.Selection(
        selection=[
            ("labor", "Labor"),
            ("material", "Material"),
            ("service", "Service"),
            ("overhead", "Overhead"),
        ],
    )
    product_uom_qty = fields.Float(
        string="Quantity", digits="Product Unit of Measure", default=1.0
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM",
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    price_unit = fields.Float(
        compute="_compute_price_unit",
        min_display_digits="Product Price",
        store=True,
        readonly=False,
    )
    margin = fields.Float(
        compute="_compute_margin",
        min_display_digits="Product Price",
        store=True,
    )
    margin_percent = fields.Float(
        string="Margin (%)",
        compute="_compute_margin",
        store=True,
    )
    unit_cost = fields.Float(
        string="Cost",
        compute="_compute_unit_cost",
        min_display_digits="Product Price",
        store=True,
        readonly=False,
        copy=False,
    )
    price_subtotal = fields.Monetary(
        string="Amount",
        compute="_compute_price_subtotal",
        store=True,
    )
    cost_subtotal = fields.Monetary(
        string="Cost Amount",
        compute="_compute_cost_subtotal",
        store=True,
    )
    tax_id = fields.Many2many(
        comodel_name="account.tax", string="Taxes", check_company=True
    )
    company_id = fields.Many2one(
        related="estimation_id.company_id",
        store=True,
    )
    currency_id = fields.Many2one(
        related="estimation_id.currency_id",
    )

    @api.depends("product_id", "company_id", "currency_id", "product_uom_id")
    def _compute_unit_cost(self):
        for line in self:
            if not line.product_id:
                line.unit_cost = 0.0
                continue
            line = line.with_company(line.company_id)

            # Convert the cost to the line UoM
            product_cost = line.product_id.uom_id._compute_price(
                line.product_id.standard_price,
                line.product_uom_id,
            )
            line.unit_cost = product_cost

    @api.depends("product_id", "company_id", "currency_id", "product_uom_id")
    def _compute_price_unit(self):
        for line in self:
            if not line.product_id:
                line.price_unit = 0.0
                continue
            line = line.with_company(line.company_id)

            # Convert the price to the line UoM
            product_price = line.product_id.uom_id._compute_price(
                line.product_id.list_price,
                line.product_uom_id,
            )
            line.price_unit = product_price

    @api.depends("product_uom_qty", "price_unit")
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.price_unit

    @api.depends("product_uom_qty", "unit_cost")
    def _compute_cost_subtotal(self):
        for line in self:
            line.cost_subtotal = line.product_uom_qty * line.unit_cost

    @api.depends("price_subtotal", "product_uom_qty", "unit_cost")
    def _compute_margin(self):
        for line in self:
            line.margin = line.price_subtotal - (line.unit_cost * line.product_uom_qty)
            line.margin_percent = (
                line.price_subtotal and line.margin / line.price_subtotal
            )

    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        """Convert the current record to a dictionary in order to use the
        generic taxes computation method defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env["account.tax"]._prepare_base_line_for_taxes_computation(
            self,
            **{
                "tax_ids": self.tax_id,
                "quantity": self.product_uom_qty,
                "partner_id": self.estimation_id.partner_id,
                "currency_id": self.estimation_id.currency_id
                or self.estimation_id.company_id.currency_id,
                # 'rate': self.estimation_id.currency_rate,
                **kwargs,
            },
        )

    @api.depends("product_id")
    def _compute_name(self):
        for line in self:
            if not line.product_id:
                continue
            line.name = (
                line.product_id.get_product_multiline_description_sale()
                or line.product_id.name
            )
