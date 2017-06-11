# -*- coding: utf-8 -*-
# © 2013 Daniel Reis
# © 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    issue_tag_id = fields.Many2one('project.tags',
                                   string='Root Tag for Issues')


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    tag_project = fields.Many2one('project.tags', string='Root Tag for Issues',
                                  compute='_compute_project_root_tag')

    @api.multi
    @api.depends('project_id')
    def _compute_project_root_tag(self):
        for issue in self:
            issue.tag_project = issue.project_id.issue_tag_id or False

    @api.onchange('project_id')
    def _onchange_project(self):
        super(ProjectIssue, self)._onchange_project_id()
        self.tag_ids &= self.project_id.issue_tag_id.child_ids
