# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ProjectIssue(models.Model):
    _inherit = 'project.issue'
    department_id = fields.Many2one('hr.department', 'Department')

    @api.onchange('project_id')
    def onchange_project(self):
        """When Project is changed: copy it's Department to the issue."""

        if self.env.context.get('project_id', None):
            project = self.env['project.project'].browse(self.env.context['project_id'])
        else:
            project = self.project_id

        if project and project.department_id:
            self.department_id = project.department_id.id
