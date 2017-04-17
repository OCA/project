# -*- coding: utf-8 -*-
# © 2014 Daniel Reis (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class Task(models.Model):
    _inherit = 'project.task'
    department_id = fields.Many2one('hr.department', 'Department')

    @api.onchange('project_id')
    def onchange_project(self):
        """ When Project is changed: copy it's Department to the issue. """

        if self.env.context.get('project_id', None):
            project = self.env['project.project'].browse(self.env.context['project_id'])
        else:
            project = self.project_id

        if project and project.department_id:
            self.department_id = project.department_id.id
