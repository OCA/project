from odoo import fields, models

class ProjectTask(models.Model):
    _inherit = 'project.task'

    priority = fields.Selection(selection_add=[('2', 'Very High')])
