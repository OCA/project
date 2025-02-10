from odoo import fields, models


class ProjectVersion(models.Model):
    _name = "project.version"
    _description = "Project Version"

    name = fields.Char(required=True)
    project_id = fields.Many2one(
        string="Project", comodel_name="project.project", required=True
    )
