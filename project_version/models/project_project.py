from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    version_ids = fields.One2many(
        comodel_name="project.version",
        inverse_name="project_id",
        string="Version",
        copy=True,
    )
