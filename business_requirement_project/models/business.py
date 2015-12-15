# -*- coding: utf-8 -*-
# © 2015
# Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessRequirement(models.Model):
    _inherit = "business.requirement"

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        ondelete='set null'
    )
    task_ids = fields.One2many(
        comodel_name='project.task',
        inverse_name='br_id',
        string='Tasks',
        copy=False
    )

    @api.multi
    def update_project_id(self, project_id):
        for br in self:
            br.project_id = project_id

    @api.multi
    def generate_project_wizard(self):
        vals = {
            'name': self.description,
            'br_id': self.id,
        }
        wizard_obj = self.env['br.generate.project']
        wizard = wizard_obj.create(vals)
        action = wizard.wizard_view()
        return action


class Project(models.Model):
    _inherit = "project.project"

    br_ids = fields.One2many(
        comodel_name='business.requirement',
        inverse_name='project_id',
        string='Business Requirement',
        copy=False,
    )
    br_count = fields.Integer(
        compute='_br_count',
        string="Business Requirement Number"
    )

    @api.one
    @api.depends('br_ids')
    def _br_count(self):
        self.br_count = len(self.br_ids)

    @api.multi
    def generate_tasks_wizard(self):
        lines = []
        for br in self.br_ids:
            for deliverables in br.deliverable_lines:
                for line in deliverables.resource_ids:
                    if line.resource_type != 'task':
                        continue
                    line = (
                        0, 0,
                        {
                            'br_id': br.id,
                            'name': line.description,
                            'sequence': line.sequence,
                            'resource_time_total': line.resource_time,
                            'user_id': line.user_id.id,
                            'select': True,
                        }
                    )
                    lines.append(line)

        vals = {
            'project_id': self.id,
            'lines': lines,
        }
        wizard_obj = self.env['br.generate.tasks']
        wizard = wizard_obj.create(vals)
        action = wizard.wizard_view()
        return action


class ProjectTask(models.Model):
    _inherit = "project.task"

    br_id = fields.Many2one(
        comodel_name='business.requirement',
        string='Business Requirement',
        ondelete='set null'
    )
