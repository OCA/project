from odoo import models, fields


class Project(models.Model):
    _inherit = 'project.project'

    project_type_id = fields.Many2one('project.type',
                                   string="Project Type",
                                   help="The type of Project",
                                   required=True)
