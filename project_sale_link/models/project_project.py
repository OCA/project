# Copyright 2025 Oihane Crucelaegui - AvanzOSC
# Copyright 2025 Mathieu Benoit - TechnoLibre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class ProjectProject(models.Model):
    _inherit = "project.project"

    sale_count = fields.Integer(compute="_compute_sale_info", string="# Sale")
    sale_line_total = fields.Monetary(
        compute="_compute_sale_info",
        string="Sale Total",
        currency_field="currency_id",
    )
    sale_invoice_count = fields.Integer(
        compute="_compute_sale_invoice_info", string="# Sale Invoice"
    )
    sale_invoice_line_total = fields.Monetary(
        compute="_compute_sale_invoice_info",
        string="Sale Invoice Total",
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Currency",
    )

    def _domain_sale_order(self):
        query = self.env["sale.order.line"]._search(
            [
                ("order_id.state", "!=", "cancel"),
            ]
        )
        # check if analytic_distribution contains id of analytic account
        query.add_where(
            "sale_order_line.analytic_distribution ?| array[%s]",
            [str(project.account_id.id) for project in self],
        )

        query.order = None
        query_string, query_param = query.select(
            "sale_order_line.order_id as order_id",
        )
        self._cr.execute(query_string, query_param)
        sale_lines_ids = list(
            set([int(record.get("order_id")) for record in self._cr.dictfetchall()])
        )
        domain = [("id", "in", sale_lines_ids)]
        return domain

    def _domain_sale_order_line(self):
        query = self.env["sale.order.line"]._search(
            [
                ("order_id.state", "!=", "cancel"),
            ]
        )
        # check if analytic_distribution contains id of analytic account
        query.add_where(
            "sale_order_line.analytic_distribution ?| array[%s]",
            [str(project.account_id.id) for project in self],
        )

        query.order = None
        query_string, query_param = query.select(
            "sale_order_line.id as id",
        )
        self._cr.execute(query_string, query_param)
        sale_lines_ids = [int(record.get("id")) for record in self._cr.dictfetchall()]
        domain = [("id", "in", sale_lines_ids)]
        return domain

    def _domain_sale_invoice(self):
        query = self.env["account.move.line"]._search(
            [
                ("move_id.state", "!=", "cancel"),
                ("move_id.move_type", "=", "out_invoice"),
            ]
        )
        # check if analytic_distribution contains id of analytic account
        ids = [str(p.account_id.id) for p in self if p.account_id]
        query.add_where(
            "account_move_line.analytic_distribution ? ANY (%s::text[])",
            (ids,),
        )
        query.order = None
        query_string, query_param = query.select(
            "DISTINCT(account_move_line.move_id) as move_id",
        )
        self._cr.execute(query_string, query_param)
        sale_invoice_ids = [
            int(record.get("move_id")) for record in self._cr.dictfetchall()
        ]
        domain = [("id", "in", sale_invoice_ids)]
        return domain

    def _domain_sale_invoice_line(self):
        query = self.env["account.move.line"]._search(
            [
                ("move_id.state", "!=", "cancel"),
                ("move_id.move_type", "=", "out_invoice"),
            ]
        )
        # check if analytic_distribution contains id of analytic account
        ids = [str(p.account_id.id) for p in self if p.account_id]
        query.add_where(
            "account_move_line.analytic_distribution ? ANY (%s::text[])",
            (ids,),
        )
        query.order = None
        query_string, query_param = query.select(
            "account_move_line.id as id",
        )
        self._cr.execute(query_string, query_param)
        sale_invoice_lines_ids = [
            int(record.get("id")) for record in self._cr.dictfetchall()
        ]
        domain = [("id", "in", sale_invoice_lines_ids)]
        return domain

    def _compute_sale_info(self):
        for project in self:
            groups = self.env["sale.order.line"].read_group(
                project._domain_sale_order_line(),
                ["price_subtotal"],
                ["order_id"],
            )
            sale_line_total = 0
            for group in groups:
                sale_line_total += group["price_subtotal"]
            project.sale_count = len(groups)
            project.sale_line_total = sale_line_total

    def _compute_sale_invoice_info(self):
        for project in self:
            groups = self.env["account.move.line"].read_group(
                project._domain_sale_invoice_line(),
                ["price_subtotal"],
                ["move_id"],
            )
            sale_invoice_line_total = 0
            for group in groups:
                sale_invoice_line_total += group["price_subtotal"]
            project.sale_invoice_count = len(groups)
            project.sale_invoice_line_total = sale_invoice_line_total

    def button_open_sale_order(self):
        self.ensure_one()
        return {
            "name": self.env._("Sale Order"),
            "domain": self._domain_sale_order(),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "sale.order",
        }

    def button_open_sale_order_line(self):
        self.ensure_one()
        return {
            "name": self.env._("Sale Order Lines"),
            "domain": self._domain_sale_order_line(),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "sale.order.line",
        }

    def button_open_sale_invoice(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )
        domain = expression.AND(
            [
                safe_eval(action.get("domain", "[]")),
                self._domain_sale_invoice(),
            ]
        )
        action.update({"domain": domain})
        return action

    def button_open_sale_invoice_line(self):
        self.ensure_one()
        return {
            "name": self.env._("Sale Invoice Lines"),
            "domain": self._domain_sale_invoice_line(),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "account.move.line",
        }
