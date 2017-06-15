# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    issue_code = fields.Char(
        string='Issue Code', required=True, default="/", readonly=True,
        copy=False)

    _sql_constraints = [
        ('project_issue_unique_code', 'UNIQUE (issue_code)',
         _('The code must be unique!')),
    ]

    @api.model
    def create(self, vals):
        if vals.get('issue_code', '/') == '/':
            vals['issue_code'] = self.env['ir.sequence'].next_by_code(
                'project.issue') or '/'
        return super(ProjectIssue, self).create(vals)
