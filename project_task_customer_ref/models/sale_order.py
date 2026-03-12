# Copyright 2026 ForgeFlow S.L.
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        # create_for_task_id is injected into the context when a sale order is
        # created directly from a task (e.g. via the "Create Sale Order" action
        # on project.task). It allows us to pre-fill client_order_ref from the
        # task's customer_reference before the SO record is saved.
        task = self.env["project.task"].browse(
            self.env.context.get("create_for_task_id")
        )
        if task and task.customer_reference:
            for vals in vals_list:
                if not vals.get("client_order_ref"):
                    vals["client_order_ref"] = task.customer_reference
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        ref = vals.get("client_order_ref")
        if ref and not self.env.context.get("_syncing_customer_reference"):
            tasks = self.env["project.task"].search([("sale_order_id", "in", self.ids)])
            tasks_to_update = tasks.filtered(lambda t: t.customer_reference != ref)
            if tasks_to_update:
                tasks_to_update.with_context(_syncing_customer_reference=True).write(
                    {"customer_reference": ref}
                )
        return res
