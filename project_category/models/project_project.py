from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    type_id = fields.Many2one(
        comodel_name='project.type',
        string='Type',
        copy=False,
        domain="[('project_ok', '=', True)]",
    )
