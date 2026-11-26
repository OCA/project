# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class ProjectRevenueRecognition(models.Model):
    _name = "project.revenue.recognition"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Project Revenue Recognition"
    _order = "name desc"

    name = fields.Char(default="/", required=True, copy=False)
    project_id = fields.Many2one(
        comodel_name="project.project",
        required=True,
        ondelete="cascade",
    )
    date = fields.Date(
        default=fields.Date.today,
        required=True,
        string="Accounting Date",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        default=lambda self: self.env.company.project_revenue_recognition_journal_id,
        required=True,
    )
    move_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="project_revenue_recognition_id",
    )
    move_count = fields.Integer(
        compute="_compute_move_count",
    )
    auto_post = fields.Boolean(default=True)
    line_ids = fields.One2many(
        comodel_name="project.revenue.recognition.line",
        inverse_name="recognition_id",
    )
    compare_with = fields.Selection(
        selection=[
            ("invoice_project", "Invoice & Project"),
        ],
        default="invoice_project",
    )
    amount_diff = fields.Monetary(
        compute="_compute_amount_diff",
        store=True,
        string="Amount Difference",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("done", "Done"),
            ("reverse", "Reverse"),
            ("cancel", "Cancel"),
        ],
        default="draft",
    )

    @api.depends("line_ids.amount", "compare_with")
    def _compute_amount_diff(self):
        for rec in self:
            if rec.compare_with == "invoice_project":
                project_amount = sum(
                    rec.line_ids.filtered(
                        lambda line: line.source_model == "project.project"
                    ).mapped("amount")
                )
                invoice_amount = sum(
                    rec.line_ids.filtered(
                        lambda line: line.source_model == "account.move"
                    ).mapped("amount")
                )
                rec.amount_diff = invoice_amount - project_amount

    def _get_project_amount(self, project_percentage):
        return project_percentage * self._get_amount_sale_invoice()[1]

    def _get_project_percentage(self):
        update = self.env["project.update"].search(
            [("project_id", "=", self.project_id.id), ("date", "<=", self.date)],
            order="date desc, id desc",
            limit=1,
        )
        return update.progress_percentage if update else 0.0

    def _prepare_project_line_vals(self):
        """Prepare line vals for project source."""
        project_percentage = self._get_project_percentage()
        project_amount = self._get_project_amount(project_percentage)
        return {
            "source_model": "project.project",
            "source_amount": self._get_amount_sale_invoice()[1],
            "amount": project_amount,
            "percent": project_percentage,
        }

    def _prepare_invoice_line_vals(self):
        """Prepare line vals for invoice source."""
        invoice_amount, so_amount_total = self._get_amount_sale_invoice()
        invoice_percentage = (
            invoice_amount / so_amount_total if so_amount_total else 0.0
        )
        return {
            "source_model": "account.move",
            "source_amount": so_amount_total,
            "amount": invoice_amount,
            "percent": invoice_percentage,
        }

    def _prepare_line_vals(self):
        """Return list of line vals dicts. Override to add new source lines."""
        self.ensure_one()
        return [
            self._prepare_project_line_vals(),
            self._prepare_invoice_line_vals(),
        ]

    def action_compare_amount(self):
        for rec in self:
            rec.line_ids.unlink()
            rec.line_ids = [Command.create(vals) for vals in rec._prepare_line_vals()]

    def _get_amount_sale_invoice(self):
        sol = self.project_id._fetch_sale_order_items(
            {"project.task": [("is_closed", "=", False)]}
        ).sudo()
        so_amount_total = sum(sol.mapped("price_subtotal"))
        analytic_account = self.project_id.account_id
        if not analytic_account:
            return 0.0, so_amount_total
        # Use raw SQL with JSONB ? operator to check analytic_distribution key
        self.env.cr.execute(
            """
            SELECT aml.id
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            WHERE am.move_type IN ('out_invoice', 'out_refund')
              AND am.state = 'posted'
              AND am.invoice_date <= %s
              AND aml.display_type = 'product'
              AND aml.analytic_distribution ? %s
            """,
            (self.date, str(analytic_account.id)),
        )
        line_ids = [row[0] for row in self.env.cr.fetchall()]
        inv_lines = self.env["account.move.line"].sudo().browse(line_ids)
        inv_amount_total = 0.0
        for line in inv_lines:
            analytic_percent = (
                line.analytic_distribution.get(str(analytic_account.id), 0) / 100
            )
            signed_amount = (
                line.price_subtotal
                if line.move_id.move_type == "out_invoice"
                else -line.price_subtotal
            )
            inv_amount_total += signed_amount * analytic_percent
        return inv_amount_total, so_amount_total

    @api.depends("move_ids")
    def _compute_move_count(self):
        for rec in self:
            rec.move_count = len(rec.move_ids)

    def _get_move_dict(self):
        self.ensure_one()
        return {
            "move_type": "entry",
            "journal_id": self.journal_id.id,
            "date": self.date,
            "ref": self.name,
            "project_revenue_recognition_id": self.id,
        }

    def _get_account_mapping(self):
        self.ensure_one()
        prec_digits = self.currency_id.decimal_places
        company = self.company_id
        project_accrued_revenue_account_id = company.project_accrued_revenue_account_id
        project_revenue_account_id = company.project_revenue_account_id
        project_deferred_revenue_account_id = (
            company.project_deferred_revenue_account_id
        )
        # Amount Diff +
        if float_compare(self.amount_diff, 0, precision_digits=prec_digits) == 1:
            debit_account, credit_account = (
                project_revenue_account_id,
                project_deferred_revenue_account_id,
            )
        # Amount Diff -
        else:
            debit_account, credit_account = (
                project_accrued_revenue_account_id,
                project_revenue_account_id,
            )
        return debit_account, credit_account

    def _get_move_line_vals_from_line(self, reverse=False):
        """Return a list of move line vals dicts for one recognition line.
        Override to customise JE lines for specific source models.
        """
        self.ensure_one()

        debit_account, credit_account = self._get_account_mapping()

        if not debit_account or not credit_account:
            return []

        amount_diff = self.amount_diff
        if reverse:
            amount_diff = -amount_diff

        amount = abs(amount_diff)

        analytic_distribution = {}
        analytic_account = self.project_id.account_id
        if analytic_account:
            analytic_distribution = {str(analytic_account.id): 100.0}

        return [
            {
                "account_id": debit_account.id,
                "name": self.name,
                "debit": amount,
                "credit": 0,
                "analytic_distribution": analytic_distribution,
            },
            {
                "account_id": credit_account.id,
                "name": self.name,
                "debit": 0,
                "credit": amount,
                "analytic_distribution": analytic_distribution,
            },
        ]

    def _get_move_line_dict(self, reverse=False):
        """Build JE lines from recognition lines. Extensible via
        _get_move_line_vals_from_line and _get_account_mapping."""
        self.ensure_one()
        move_line_vals = self._get_move_line_vals_from_line(reverse)
        return [Command.create(vals) for vals in move_line_vals]

    def _create_moves(self, reverse=False):
        move_dict = []
        for rec in self:
            move = rec._get_move_dict()
            move["line_ids"] = rec._get_move_line_dict(reverse)
            move_dict.append(move)
        moves = self.env["account.move"].create(move_dict)
        return moves

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                name = (
                    self.env["ir.sequence"].next_by_code("project.revenue.recognition")
                    or "/"
                )
                vals["name"] = name
        return super().create(vals_list)

    def action_confirm(self):
        if any(not rec.line_ids for rec in self):
            raise UserError(self.env._("Please compare amount first."))
        return self.write({"state": "confirm"})

    def action_adjust_cost(self):
        moves = self._create_moves()
        if self.auto_post:
            moves._post()
        return self.write({"state": "done"})

    def action_reverse_cost(self):
        moves = self.move_ids.filtered(lambda m: m.state == "posted")
        action = moves.with_context(active_ids=moves.ids).action_reverse()
        action["context"] = {"active_model": moves._name, "active_ids": moves.ids}
        return action

    def action_reverse(self):
        return self.write({"state": "reverse"})

    def action_cancel(self):
        # NOTE: Cancel is not implemented
        return self.write({"state": "cancel"})

    def action_draft(self):
        return self.write({"state": "draft"})

    def action_view_move(self):
        self.ensure_one()
        action = {
            "name": self.env._("Journal Entries"),
            "view_mode": "list,form",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.move_ids.ids)],
            "views": [
                [self.env.ref("account.view_move_tree").id, "list"],
                [self.env.ref("account.view_move_form").id, "form"],
            ],
        }
        return action


class ProjectRevenueRecognitionLine(models.Model):
    _name = "project.revenue.recognition.line"
    _description = "Project Revenue Recognition Line"

    recognition_id = fields.Many2one(
        comodel_name="project.revenue.recognition",
        index=True,
        required=True,
        ondelete="cascade",
    )
    source_model = fields.Selection(
        selection=[
            ("project.project", "Project"),
            ("account.move", "Invoice"),
        ],
        required=True,
    )
    source_amount = fields.Monetary()
    amount = fields.Monetary()
    percent = fields.Float()
    company_id = fields.Many2one(
        related="recognition_id.company_id",
        store=True,
    )
    currency_id = fields.Many2one(
        related="recognition_id.currency_id",
        store=True,
    )
