from odoo import fields, models


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    project_role_id = fields.Many2one(
        "project.role",
    )
