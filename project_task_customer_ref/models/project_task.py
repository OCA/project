# Copyright 2026 ForgeFlow S.L.
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    customer_reference = fields.Char(string="Order Customer Reference", copy=False)

    def _get_linked_sale_order(self):
        """Return the sale order linked to this task (via line or project)."""
        self.ensure_one()
        return self.sale_order_id or self.project_id.sale_order_id

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        if not self.env.context.get("_syncing_customer_reference"):
            for task, vals in zip(tasks, vals_list, strict=False):
                ref = vals.get("customer_reference")
                if ref:
                    so = task._get_linked_sale_order()
                    if so and so.client_order_ref != ref:
                        so.with_context(
                            _syncing_customer_reference=True
                        ).client_order_ref = ref
        return tasks

    def write(self, vals):
        res = super().write(vals)
        ref = vals.get("customer_reference")
        if ref and not self.env.context.get("_syncing_customer_reference"):
            for task in self:
                so = task._get_linked_sale_order()
                if so and so.client_order_ref != ref:
                    so.with_context(
                        _syncing_customer_reference=True
                    ).client_order_ref = ref
        return res
