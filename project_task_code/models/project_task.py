# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, fields, models, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    code = fields.Char(
        string='Task Number', required=True, default="/", readonly=True)

    _sql_constraints = [
        ('project_task_unique_code', 'UNIQUE (code)',
         _('The code must be unique!')),
    ]

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].get('project.task')
        return super(ProjectTask, self).create(vals)

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = self.env['ir.sequence'].get('project.task')
        return super(ProjectTask, self).copy(default)
