# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    order_line_link_ids = fields.Many2many(
        "sale.order.line",
        "project_project_sale_order_line_related_rel",
        compute="_compute_order_link_ids",
        compute_sudo=True,
        store=True,
    )
    sale_order_link_ids = fields.Many2many(
        "sale.order",
        "project_project_sale_order_related_rel",
        compute="_compute_order_link_ids",
        compute_sudo=True,
        store=True,
    )

    @api.depends(
        "sale_line_id",
        "task_ids.sale_line_id",
        "timesheet_ids.so_line",
        "sale_line_employee_ids.sale_line_id",
    )
    def _compute_order_link_ids(self):
        for project in self:
            order_lines = self.env["sale.order.line"]
            order_lines |= (
                project.sale_line_id
                | project.task_ids.sale_line_id
                | project.timesheet_ids.so_line
                | project.sale_line_employee_ids.sale_line_id
            )
            project.order_line_link_ids = order_lines.ids
            project.sale_order_link_ids = order_lines.order_id.ids

    def action_view_so_link(self):
        self.ensure_one()
        so_ids = self.with_context().sale_order_link_ids.ids
        action_window = {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "name": "Sales Order",
            "views": [[False, "tree"], [False, "form"]],
            "context": {"create": False, "show_sale": True},
            "domain": [["id", "in", so_ids]],
        }
        if len(so_ids) == 1:
            action_window["views"] = [[False, "form"]]
            action_window["res_id"] = so_ids[0]

        return action_window
