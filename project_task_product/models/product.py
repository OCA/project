# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    task_count = fields.Integer(compute="_compute_task_count")

    def _compute_task_count(self):
        task_data = self.env["project.task"]._read_group(
            [("product_id", "in", self.ids)],
            groupby=["product_id"],
            aggregates=["__count"],
        )
        mapped = {product.id: count for product, count in task_data}
        for product in self:
            product.task_count = mapped.get(product.id, 0)

    def action_view_tasks(self):
        action = self.env["ir.actions.actions"]._for_xml_id("project.action_view_task")
        action.update(
            {
                "domain": [("product_id", "in", self.ids)],
                "context": {"default_product_id": self.id},
            }
        )
        return action


class ProductTemplate(models.Model):
    _inherit = "product.template"

    task_count = fields.Integer(compute="_compute_task_count")

    def _compute_task_count(self):
        variants = self.mapped("product_variant_ids")

        task_data = self.env["project.task"]._read_group(
            [("product_id", "in", variants.ids)],
            groupby=["product_id"],
            aggregates=["__count"],
        )

        mapped = {product.id: count for product, count in task_data}

        for template in self:
            template.task_count = sum(
                mapped.get(variant.id, 0) for variant in template.product_variant_ids
            )

    def action_view_tasks(self):
        action = self.env["ir.actions.actions"]._for_xml_id("project.action_view_task")
        action["domain"] = [("product_id", "in", self.product_variant_ids.ids)]
        return action
