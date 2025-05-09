# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class ProjectProject(models.Model):
    _inherit = "project.project"

    purchase_count = fields.Integer(
        compute="_compute_purchase_info", string="# Purchase"
    )
    purchase_line_total = fields.Integer(
        compute="_compute_purchase_info", string="Purchase Total"
    )
    purchase_invoice_count = fields.Integer(
        compute="_compute_purchase_invoice_info", string="# Purchase Invoice"
    )
    purchase_invoice_line_total = fields.Float(
        compute="_compute_purchase_invoice_info", string="Purchase Invoice Total"
    )

    def _domain_purchase_order(self):
        query = self.env["purchase.order.line"]._search(
            [
                ("order_id.state", "!=", "cancel"),
            ]
        )
        # check if analytic_distribution contains id of analytic account
        query.add_where(
            "purchase_order_line.analytic_distribution ?| array[%s]",
            [str(project.account_id.id) for project in self],
        )

        query.order = None
        query_string, query_param = query.select(
            "purchase_order_line.order_id as order_id",
        )
        self._cr.execute(query_string, query_param)
        purchase_lines_ids = [
            int(record.get("order_id")) for record in self._cr.dictfetchall()
        ]
        domain = [("id", "in", purchase_lines_ids)]
        return domain

    def _domain_purchase_order_line(self):
        query = self.env["purchase.order.line"]._search(
            [
                ("order_id.state", "!=", "cancel"),
            ]
        )
        # check if analytic_distribution contains id of analytic account
        query.add_where(
            "purchase_order_line.analytic_distribution ?| array[%s]",
            [str(project.account_id.id) for project in self],
        )

        query.order = None
        query_string, query_param = query.select(
            "purchase_order_line.id as id",
        )
        self._cr.execute(query_string, query_param)
        purchase_lines_ids = [
            int(record.get("id")) for record in self._cr.dictfetchall()
        ]
        domain = [("id", "in", purchase_lines_ids)]
        return domain

    def _domain_purchase_invoice(self):
        query = self.env["account.move.line"]._search(
            [
                ("move_id.state", "!=", "cancel"),
            ]
        )
        # check if analytic_distribution contains id of analytic account
        query.add_where(
            "account_move_line.analytic_distribution ?| array[%s]",
            [str(project.account_id.id) for project in self],
        )
        query.order = None
        query_string, query_param = query.select(
            "DISTINCT(account_move_line.move_id) as move_id",
        )
        self._cr.execute(query_string, query_param)
        purchase_invoice_ids = [
            int(record.get("move_id")) for record in self._cr.dictfetchall()
        ]
        domain = [("id", "in", purchase_invoice_ids)]
        return domain

    def _domain_purchase_invoice_line(self):
        query = self.env["account.move.line"]._search(
            [
                ("move_id.state", "!=", "cancel"),
                ("move_id.move_type", "=", "in_invoice"),
            ]
        )
        # check if analytic_distribution contains id of analytic account
        query.add_where(
            "account_move_line.analytic_distribution ?| array[%s]",
            [str(project.account_id.id) for project in self],
        )
        query.order = None
        query_string, query_param = query.select(
            "account_move_line.id as id",
        )
        self._cr.execute(query_string, query_param)
        purchase_invoice_lines_ids = [
            int(record.get("id")) for record in self._cr.dictfetchall()
        ]
        domain = [("id", "in", purchase_invoice_lines_ids)]
        return domain

    def _compute_purchase_info(self):
        for project in self:
            groups = self.env["purchase.order.line"].read_group(
                project._domain_purchase_order_line(),
                ["order_id"],
                ["price_subtotal"],
            )
            purchase_line_total = 0
            for group in groups:
                purchase_line_total += group["price_subtotal"]
            project.purchase_count = len(groups)
            project.purchase_line_total = purchase_line_total

    def _compute_purchase_invoice_info(self):
        for project in self:
            groups = self.env["account.move.line"].read_group(
                project._domain_purchase_invoice_line(),
                ["price_subtotal"],
                ["move_id"],
            )
            purchase_invoice_line_total = 0
            for group in groups:
                purchase_invoice_line_total += group["price_subtotal"]
            project.purchase_invoice_count = len(groups)
            project.purchase_invoice_line_total = purchase_invoice_line_total

    def button_open_purchase_order(self):
        self.ensure_one()
        return {
            "name": self.env._("Purchase Order"),
            "domain": self._domain_purchase_order(),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "purchase.order",
        }

    def button_open_purchase_order_line(self):
        self.ensure_one()
        return {
            "name": self.env._("Purchase Order Lines"),
            "domain": self._domain_purchase_order_line(),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "purchase.order.line",
        }

    def button_open_purchase_invoice(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_in_invoice_type"
        )
        domain = expression.AND(
            [
                safe_eval(action.get("domain", "[]")),
                self._domain_purchase_invoice(),
            ]
        )
        action.update({"domain": domain})
        return action

    def button_open_purchase_invoice_line(self):
        self.ensure_one()
        return {
            "name": self.env._("Purchase Invoice Lines"),
            "domain": self._domain_purchase_invoice_line(),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "account.move.line",
        }
