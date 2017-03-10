# -*- coding: utf-8 -*-
# © 2013 Daniel Reis
# © 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _


class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    task_tag_id = fields.Many2one('project.tags', string='Root Tag for Tasks')
    

class ProjectCategory(models.Model):
    _inherit = 'project.tags'
    _order = 'parent_id,name'
    _rec_name = 'complete_name'

    parent_id = fields.Many2one('project.tags', string='Parent Tag', index=True)
    child_ids = fields.One2many('project.tags', 'parent_id', 
                                string='Child Categories')
    complete_name = fields.Char(string='Name', compute='_compute_complete_name')
    code = fields.Char(string='Code', size=10)

    @api.multi
    @api.depends('name', 'parent_id')
    def _compute_complete_name(self):
        for tag in self:
            parent_name = tag.parent_id.name and tag.parent_id.name + ' / '
            tag.complete_name = (parent_name or '') + tag.name
    

class ProjectTask(models.Model):
    _inherit = 'project.task'

    tag_project = fields.Many2one('project.tags', string='Root Tag',
                                  compute='_compute_project_task_tag')

    @api.multi
    @api.depends('project_id')
    def _compute_project_task_tag(self):
        for tag in self:
            tag.tag_project = self.project_id.task_tag_id or False
    
    @api.onchange('project_id')
    def _onchange_project(self):
        res = super(ProjectTask, self)._onchange_project()
        self.tag_ids &= self.project_id.task_tag_id.child_ids

