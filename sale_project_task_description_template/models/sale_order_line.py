# Copyright 2025 NICO SOLUTIONS - ENGINEERING & IT
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_task_prepare_values(self, project):
        values = super()._timesheet_create_task_prepare_values(project)

        product = self.product_id.product_tmpl_id
        template = product.task_description_template_id

        if template:
            values["description_template_id"] = template.id

        if product.include_sale_line_info_in_task:
            product_info = self.env._(
                "%(product)s - Qty: %(qty)s",
                product=self.product_id.name,
                qty=self.product_uom_qty,
            )

            if template and template.description:
                values["description"] = f"{product_info}\n\n{template.description}"
            else:
                values["description"] = product_info
        elif template and template.description:
            values["description"] = template.description

        return values
