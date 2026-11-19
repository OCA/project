# Copyright 2025 NICO SOLUTIONS - ENGINEERING & IT
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    task_description_template_id = fields.Many2one(
        "project.task.description.template",
        string="Task Description Template",
        help="Applies automatically when creating tasks",
    )

    include_sale_line_info_in_task = fields.Boolean(
        string="Include Sale Line Info in Task description",
        help="If enabled, the sale order line details (e.g., product and quantity) "
        "will be added to the task description before the template content.",
    )
