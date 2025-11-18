# Copyright 2023 - Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    description_template_id = fields.Many2one(
        "project.task.description.template", store=False
    )

    @api.onchange("description_template_id")
    def _onchange_description_template_id(self):
        for task in self:
            if not task.description_template_id:
                continue
            template_text = task.description_template_id.description or ""
            # fields are html, str and compare them
            template_text = str(template_text)
            current = task.description or ""
            current = str(current)
            # Avoid duplicating the same template content ANYWHERE in the description
            if current == template_text or template_text in current:
                continue
            task.description = current + template_text
