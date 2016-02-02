# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Michael Viriyananda
#    Copyright 2016 OpenSynergy Indonesia
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
