# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class ProjectTaskTemplate(models.Model):
    _name = "project.task.template"
    _description = "Project Task Template"

    name = fields.Char()
    tag_ids = fields.Many2many(comodel_name="project.tags")
    user_id = fields.Many2one(string="Assigned to", comodel_name="res.users")
    description = fields.Html()
    project_ids = fields.Many2many(comodel_name="project.project")
