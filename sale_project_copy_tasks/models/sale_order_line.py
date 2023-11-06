# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_service_generation(self):
        """Adds task inheritance from project_templates

        Creates the project in sale order if needed and copies tasks
        from product project_template to order project.
        """
        so_model = self.env["sale.order"]
        mt_note = self.env.ref("mail.mt_note")
        # Check lines that need to inherit project template tasks
        sol_copy_tasks = self.filtered(
            lambda sol: sol.is_service
            and sol.product_id.service_tracking == "copy_tasks_in_project"
            and sol.product_id.project_template_id
        )
        # Remove lines with tasks
        sol_copy_tasks -= (
            self.env["project.task"]
            .sudo()
            .search(
                [
                    ("sale_line_id", "in", sol_copy_tasks.ids),
                ]
            )
            .mapped("sale_line_id")
        )

        # Create sale order projects automatically
        # for lines that don't have projects associated
        new_projects = (
            sol_copy_tasks.filtered(lambda sol: not sol.order_id.project_id)
            .mapped("order_id")
            .create_order_project()
        )

        # Copy task from line template_projects if don't have one associated
        orders_linked = so_model.browse()
        for sol_to_copy_task in sol_copy_tasks:
            order = sol_to_copy_task.order_id
            target_project = sol_to_copy_task.project_id or order.project_id
            # If line don't have associated project, assign to it
            sol_to_copy_task.project_id = target_project
            # Notify order on project
            if target_project not in new_projects and order not in orders_linked:
                target_project.sudo().message_post_with_view(
                    "mail.message_origin_link",
                    values={"self": target_project, "origin": order},
                    subtype_id=mt_note.id,
                )
                orders_linked |= order
            default_task_data = {
                "project_id": sol_to_copy_task.project_id.id,
                "sale_line_id": sol_to_copy_task.id,
                "sale_order_id": order.id,
                "partner_id": order.partner_id.id,
                "email_from": order.partner_id.email,
                "date_deadline": order.commitment_date,
                "active": True,
            }
            tasks = sol_to_copy_task.product_id.project_template_id.with_context(
                active_test=False
            ).tasks
            for task in tasks:
                task.copy(
                    dict(
                        default_task_data,
                        name=task.name,
                        stage_id=task.stage_id.id,
                    )
                )
        return super()._timesheet_service_generation()
