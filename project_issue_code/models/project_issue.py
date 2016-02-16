# -*- coding: utf-8 -*-
# © 2016 Michael Viriyananda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    issue_code = fields.Char(
        string='Issue Code', required=True, default="/", readonly=True)

    _sql_constraints = [
        ('project_issue_unique_code', 'UNIQUE (issue_code)',
         _('The code must be unique!')),
    ]

    @api.model
    def create(self, vals):
        if vals.get('issue_code', '/') == '/':
            vals['issue_code'] = self.env['ir.sequence'].get('project.issue')
        return super(ProjectIssue, self).create(vals)

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['issue_code'] = self.env['ir.sequence'].get('project.issue')
        return super(ProjectIssue, self).copy(default)
