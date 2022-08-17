# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class ProjectProject(models.Model):

    _inherit = "project.project"

    sale_order_count = fields.Integer(
        compute="_compute_sale_order_count", string="# of Sale Order"
    )

    customer_invoice_count = fields.Integer(
        compute="_compute_customer_invoice_count", string="# of Customer Invoice"
    )

    def _compute_sale_order_count(self):
        group_data = self.env["sale.order"].read_group(
            self._get_sale_order_domain(), ["project_id"], ["project_id"]
        )
        count_by_id = {
            data["project_id"][0]: data["project_id_count"] for data in group_data
        }
        for rec in self:
            rec.sale_order_count = count_by_id.get(rec.id, 0)

    def action_open_sale_orders(self):
        self.ensure_one()
        action = self.env.ref("sale.action_quotations_with_onboarding").read([])[0]
        action.update(
            {
                "domain": self._get_sale_order_domain(),
                "context": {"default_project_id": self.id},
            }
        )
        return action

    def _get_sale_order_domain(self):
        return [("project_id", "in", self.ids)]

    def _compute_customer_invoice_count(self):
        domain = self._get_sale_invoice_line_domain()
        group_data = self.env["account.move.line"].read_group(
            domain, ["move_id:count_distinct"], ["analytic_account_id"],
        )
        count_by_id = {
            data["analytic_account_id"][0]: data["move_id"] for data in group_data
        }
        for project in self:
            project.customer_invoice_count = count_by_id.get(
                project.analytic_account_id.id, 0
            )

    def _get_sale_invoice_line_domain(self):
        return [
            ("analytic_account_id", "in", self.mapped("analytic_account_id").ids,),
            ("move_id.type", "in", ("out_invoice", "out_refund")),
        ]

    def action_open_customer_invoice(self):
        self.ensure_one()
        action = self.env.ref("account.action_move_line_form")
        action_dict = action.read()[0] if action else {}
        lines = self.env["account.move.line"].search(
            self._get_sale_invoice_line_domain()
        )
        domain = expression.AND(
            [
                [("id", "in", lines.mapped("move_id").ids)],
                safe_eval(action.domain or "[]"),
            ]
        )
        action_dict.update({"domain": domain})
        return action_dict
