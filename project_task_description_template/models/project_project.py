# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    task_template_ids = fields.Many2many(
        string="Task Templates", comodel_name="project.task.template"
    )

    template_task_type_ids = fields.Many2many(
        string="Available in", comodel_name="project.task.type"
    )
