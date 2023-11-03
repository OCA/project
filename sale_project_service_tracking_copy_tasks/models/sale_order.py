# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("order_line.product_id.service_tracking")
    def _compute_visible_project(self):
        """Users should be able to select a project_id on the order if
        at least one order line has a product with
        its service tracking configured as 'copy_tasks_in_project'"""
        super()._compute_visible_project()
        for order in self:
            if any(
                service_tracking == "copy_tasks_in_project"
                for service_tracking in order.order_line.mapped(
                    "product_id.service_tracking"
                )
            ):
                order.visible_project = True

    def _get_order_project_data(self):
        self.ensure_one()
        if not self.analytic_account_id:
            self._create_analytic_account()
        return dict(
            partner_id=self.partner_id.id,
            sale_order_id=self.id,
            analytic_account_id=self.analytic_account_id.id,
            name=self.name,
        )

    @api.returns("project.project")
    def create_order_project(self):
        pp_model = self.env["project.project"]
        created_projects = pp_model.browse()
        for order in self:
            projects = order.mapped("order_line.product_id.project_template_id")
            project_data = projects[0].copy_data(
                default=dict(
                    type_ids=projects.mapped("type_ids").ids,
                    subtask_project_id=False,
                    active=True,
                    **order._get_order_project_data(),
                )
            )
            new_project = pp_model.create(project_data)
            created_projects |= new_project
            order.project_id = new_project
            new_project.analytic_account_id.partner_id = order.partner_id
            order._onchange_project_id()
            new_project.sudo().message_post_with_view(
                "mail.message_origin_link",
                values={"self": order.project_id, "origin": order},
                subtype_id=self.env.ref("mail.mt_note").id,
            )
        return created_projects
