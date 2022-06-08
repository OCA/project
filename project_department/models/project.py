from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    project_department_id = fields.Many2one(
        related='project_id.department_id',
        string='Project Department',
        store=True,
        readonly=True)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Project Department')
