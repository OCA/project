# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProjectEstimation(models.Model):
    _name = "project.estimation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Project Estimation"
    _order = "name desc"

    name = fields.Char(
        default="/",
        required=True,
        copy=False,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
        tracking=True,
    )
    project_id = fields.Many2one(
        comodel_name="project.project",
        tracking=True,
    )
    sale_order_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="project_estimation_id",
        copy=False,
    )
    date = fields.Date(
        string="Estimation Date",
        default=fields.Date.today,
        required=True,
        tracking=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        default=lambda self: self.env.user,
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        compute="_compute_currency_id",
        store=True,
    )
    line_ids = fields.One2many(
        comodel_name="project.estimation.line",
        inverse_name="estimation_id",
        string="Estimation Lines",
        copy=True,
    )

    amount_untaxed = fields.Monetary(
        string="Untaxed Amount", store=True, compute="_compute_amounts", tracking=5
    )
    amount_tax = fields.Monetary(string="Taxes", store=True, compute="_compute_amounts")
    amount_total = fields.Monetary(
        string="Total", store=True, compute="_compute_amounts", tracking=4
    )

    total_cost = fields.Monetary(
        compute="_compute_totals",
        store=True,
    )
    total_margin = fields.Monetary(
        compute="_compute_totals",
        store=True,
    )
    total_margin_percent = fields.Float(
        string="Total Margin (%)",
        compute="_compute_totals",
        store=True,
    )
    target_margin = fields.Float(
        string="Target Margin (%)",
    )
    target_sale_price = fields.Monetary(
        compute="_compute_target_sale_price",
        store=True,
    )
    expected_profit = fields.Monetary(
        compute="_compute_expected_profit",
        store=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("approved", "Approved"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )
    note = fields.Html(string="Notes")

    @api.depends("line_ids.price_subtotal", "currency_id", "company_id")
    def _compute_amounts(self):
        AccountTax = self.env["account.tax"]
        for rec in self:
            lines = rec.line_ids.filtered(lambda x: not x.display_type)
            base_lines = [
                line._prepare_base_line_for_taxes_computation() for line in lines
            ]
            AccountTax._add_tax_details_in_base_lines(base_lines, rec.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, rec.company_id)
            tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=rec.currency_id or rec.company_id.currency_id,
                company=rec.company_id,
            )
            rec.amount_untaxed = tax_totals["base_amount_currency"]
            rec.amount_tax = tax_totals["tax_amount_currency"]
            rec.amount_total = tax_totals["total_amount_currency"]

    @api.depends("company_id")
    def _compute_currency_id(self):
        for rec in self:
            rec.currency_id = rec.company_id.currency_id

    @api.depends("line_ids.price_subtotal", "line_ids.margin", "line_ids.cost_subtotal")
    def _compute_totals(self):
        for rec in self:
            rec.total_cost = sum(rec.line_ids.mapped("cost_subtotal"))
            rec.total_margin = sum(rec.line_ids.mapped("margin"))
            rec.total_margin_percent = (
                rec.amount_untaxed and rec.total_margin / rec.amount_untaxed
            )

    @api.depends("total_cost", "target_margin")
    def _compute_target_sale_price(self):
        for rec in self:
            margin = rec.target_margin
            if margin >= 100:
                rec.target_sale_price = 0.0
            elif margin > 0:
                rec.target_sale_price = rec.total_cost / (1 - margin / 100)
            else:
                rec.target_sale_price = rec.total_cost

    @api.depends("target_sale_price", "total_cost")
    def _compute_expected_profit(self):
        for rec in self:
            rec.expected_profit = rec.target_sale_price - rec.total_cost

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("project.estimation") or "/"
                )
        return super().create(vals_list)

    def action_confirm(self):
        return self.write({"state": "confirm"})

    def action_approve(self):
        return self.write({"state": "approved"})

    def action_cancel(self):
        return self.write({"state": "cancelled"})

    def action_done(self):
        return self.write({"state": "done"})

    def action_draft(self):
        return self.write({"state": "draft"})

    def action_create_sale_order(self):
        """Open wizard to create a Sale Order from the estimation."""
        self.ensure_one()
        if not self.line_ids:
            raise UserError(self.env._("Please add at least one estimation line."))
        return {
            "name": self.env._("Create Sale Order"),
            "type": "ir.actions.act_window",
            "res_model": "project.estimation.create.sale.order",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_estimation_id": self.id,
            },
        }

    def action_view_sale_order(self):
        self.ensure_one()
        return {
            "name": self.env._("Sale Order"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "list,form",
            "domain": [("project_estimation_id", "=", self.id)],
        }

    def action_view_project(self):
        self.ensure_one()
        return {
            "name": self.env._("Project"),
            "type": "ir.actions.act_window",
            "res_model": "project.project",
            "view_mode": "form",
            "res_id": self.project_id.id,
        }
