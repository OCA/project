# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class TaskTemplate(models.Model):
    _name = "project.task.template"

    name = fields.Char(string="Name")
    tag_ids = fields.Many2many(string="Tags", comodel_name="project.tags")
    user_id = fields.Many2one(string="Assigned to", comodel_name="res.users")
    description = fields.Html(string="Description")
    project_ids = fields.Many2many(string="Projects", comodel_name="project.project")
