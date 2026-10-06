from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    version_id = fields.Many2one(
        comodel_name="project.version",
        copy=True,
    )
