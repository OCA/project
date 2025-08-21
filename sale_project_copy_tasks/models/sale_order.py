# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("order_line.product_id.service_tracking")
    def _compute_visible_project(self):
        """Let users select a project on matching orders.

        Affects orders where at least one line has a product with
        its service tracking configured as 'copy_tasks_in_project'.
        """
        result = super()._compute_visible_project()
        for order in self:
            order.visible_project = "copy_tasks_in_project" in order.order_line.mapped(
                "product_id.service_tracking"
            )
        return result

    def _get_order_project_data(self):
        self.ensure_one()
        return dict(
            partner_id=self.partner_id.id,
            sale_order_id=self.id,
            account_id=self.env.context.get("project_account_id")
            or self.project_account_id.id
            or self.env["account.analytic.account"]
            .create(self._prepare_analytic_account_data())
            .id,
            name=self.name,
        )

    @api.returns("project.project")
    def create_order_project(self):
        pp_model = self.env["project.project"]
        created_projects = pp_model.browse()
        for order in self:
            projects = order.mapped("order_line.product_id.project_template_id")
            new_project = projects[0].copy(
                dict(
                    type_ids=projects.mapped("type_ids").ids,
                    active=True,
                    tasks=False,
                    **order._get_order_project_data(),
                )
            )
            created_projects |= new_project
            order.project_id = new_project
            new_project.account_id.partner_id = order.partner_id
            new_project.sudo().message_post_with_source(
                "mail.message_origin_link",
                render_values={"self": new_project, "origin": order},
                subtype_xmlid="mail.mt_note",
            )
        return created_projects
