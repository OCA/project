# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _


class BrGenerateTasks(models.TransientModel):
    _name = 'br.generate.tasks'
    _description = 'Generate Tasks'

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        ondelete='set null'
    )

    lines = fields.One2many(
        comodel_name='br.generate.tasks.line',
        inverse_name='wizard_id',
        string='Generate Tasks Lines',
    )

    @api.multi
    def wizard_view(self):
        view = self.env['ir.model.data'].get_object_reference(
            'business_requirement_project', 'view_br_generate_tasks_form')

        action = {
            'name': _('Generate Tasks'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'views': [(view[1], 'form')],
            'view_id': view[1],
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context,
        }
        return action

    @api.multi
    def apply(self):
        tasks = self.generate_tasks()
        task_ids = [str(x.id) for x in tasks]

        view = self.env['ir.model.data'].get_object_reference(
            'project', 'view_task_tree2')

        action = {
            'domain': "[('id','in',[%s])]" % ','.join(task_ids),
            'name': _('Tasks'),
            'view_type': 'tree',
            'view_mode': 'list',
            'res_model': 'project.task',
            'view_id': view[1],
            'type': 'ir.actions.act_window'
        }

        return action

    @api.multi
    def _prepare_project_task(self, line):
        task = {
            'br_resource_id': line.br_resource_id.id,
            'name': line.name,
            'description': line.description,
            'sequence': line.sequence,
            'project_id': self.project_id.id,
            'planned_hours': line.resource_time_total,
        }
        return task

    @api.multi
    def generate_tasks(self):
        task_obj = self.env['project.task']
        tasks = []
        for line in self.lines:
            task_val = self._prepare_project_task(line)
            task = task_obj.create(task_val)
            tasks.append(task)
        return tasks


class BrGenerateTasksLine(models.TransientModel):
    _name = 'br.generate.tasks.line'
    _description = 'Generate Tasks Lines'

    sequence = fields.Integer('Sequence')
    name = fields.Char('Task Name')
    description = fields.Char('Description')
    resource_time_total = fields.Float(
        string='Total Resouce time',
        help='Sum up all the time of the resouce of each resouce line.'
    )
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='UoM',
        required=True
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Default User'
    )
    wizard_id = fields.Many2one(
        comodel_name='br.generate.tasks',
        string='Wizard'
    )
    br_id = fields.Many2one(
        comodel_name='business.requirement',
        string='Business Requirement',
        copy=False
    )
    br_resource_id = fields.Many2one(
        comodel_name='business.requirement.resource',
        string='Business Requirement Resource',
        ondelete='set null'
    )
