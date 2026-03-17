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
    unit_cost = fields.Float(
        string="Cost",
        compute="_compute_unit_cost",
        min_display_digits="Product Price",
        store=True,
        readonly=False,
        copy=False,
    )
    cost_ratio = fields.Float(
        string="Cost Ratio (%)",
        inverse="_inverse_cost_ratio",
        store=True,
        copy=False,
    )
    price_unit = fields.Float(
        string="Sale Price",
        compute="_compute_price_unit",
        inverse="_inverse_price_unit",
        store=True,
        min_display_digits="Product Price",
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
    discount = fields.Float(
        string="Disc.%",
        digits="Discount",
    )
    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits="Product Price",
        help="Fixed amount discount.",
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

    def _inverse_cost_ratio(self):
        for rec in self:
            if rec.cost_ratio:
                rec.price_unit = rec.unit_cost / rec.cost_ratio

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

    def _inverse_price_unit(self):
        for rec in self:
            if rec.price_unit <= 0:
                rec.cost_ratio = 0.0
            else:
                rec.cost_ratio = rec.unit_cost / rec.price_unit

    @api.depends(
        "product_uom_qty", "discount", "discount_fixed", "price_unit", "tax_id"
    )
    def _compute_price_subtotal(self):
        for line in self:
            base_line = line._prepare_base_line_for_taxes_computation()
            self.env["account.tax"]._add_tax_details_in_base_line(
                base_line, line.company_id
            )
            line.price_subtotal = base_line["tax_details"][
                "raw_total_excluded_currency"
            ]

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

    @api.onchange("discount_fixed")
    def _onchange_discount_fixed(self):
        for line in self:
            if line.discount_fixed:
                line.discount = 0.0

    @api.onchange("discount")
    def _onchange_discount(self):
        for line in self:
            if line.discount:
                line.discount_fixed = 0.0

    def _get_discount_from_fixed_discount(self):
        """Calculate the discount percentage from the fixed discount amount."""
        self.ensure_one()
        if not self.discount_fixed:
            return self.discount

        return (
            (self.price_unit != 0)
            and ((self.discount_fixed) / self.price_unit) * 100
            or 0.00
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
                "discount": self._get_discount_from_fixed_discount(),
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
