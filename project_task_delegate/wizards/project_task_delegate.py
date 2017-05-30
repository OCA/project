# -*- coding: utf-8 -*-
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree

from openerp import tools
from openerp.tools.translate import _
from openerp import models, fields, api


class ProjectTaskDelegate(models.TransientModel):
    _name = 'project.task.delegate'
    _description = 'Task Delegate'

    name = fields.Char('Delegated Title', required=True,
                       help="New title of the task delegated to the user")
    prefix = fields.Char(
        'Your Task Title', help="Title for your validation task")
    project_id = fields.Many2one(
        'project.project',
        'Project',
        help="User you want to delegate this task to")
    user_id = fields.Many2one('res.users', 'Assign To', required=True,
                              help="User you want to delegate this task to")
    new_task_description = fields.Text(
        'New Task Description',
        help="Reinclude the description of the task in the task of the user")
    planned_hours = fields.Float(
        'Planned Hours',
        default=1.0,
        help="Estimated time to close this task by the delegated user")
    planned_hours_me = fields.Float(
        'Hours to Validate',
        help="""Estimated time for you to validate the work done
             by the user to whom you delegate this task""")
    state = fields.Selection([('pending', 'Pending'), ('done', 'Done'), ],
                             'Validation State', default='pending',
                             help="""New state of your own task. Pending will be
             reopened automatically when the delegated task is closed""")

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.user_id = self.project_id.user_id.id

    @api.model
    def default_get(self, fields):
        """
        This function gets default values
        """
        res = super(ProjectTaskDelegate, self).default_get(fields)
        record_id = self.env.context.get('active_id')
        task = self.env['project.task'].browse(record_id)
        task_name = tools.ustr(task.name)

        if 'project_id' in fields:
            res['project_id'] = int(
                task.project_id.id) if task.project_id else False

        if 'name' in fields:
            if task_name.startswith(_('CHECK: ')):
                newname = tools.ustr(task_name).replace(_('CHECK: '), '')
            else:
                newname = tools.ustr(task_name or '')
            res['name'] = newname
        if 'planned_hours' in fields:
            res['planned_hours'] = task.remaining_hours or 0.0
        if 'prefix' in fields:
            if task_name.startswith(_('CHECK: ')):
                newname = tools.ustr(task_name).replace(_('CHECK: '), '')
            else:
                newname = tools.ustr(task_name or '')
            prefix = _('CHECK: %s') % newname
            res['prefix'] = prefix
        if 'new_task_description' in fields:
            res['new_task_description'] = task.description
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(ProjectTaskDelegate, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        obj_tm = self.env['res.users'].browse(
            self._uid).company_id.project_time_mode_id
        tm = obj_tm and obj_tm.name or 'Hours'
        if tm in ['Hours', 'Hour']:
            return res

        eview = etree.fromstring(res['arch'])

        def _check_rec(eview):
            if eview.attrib.get('widget', '') == 'float_time':
                eview.set('widget', 'float')
            for child in eview:
                _check_rec(child)
            return True

        _check_rec(eview)
        res['arch'] = etree.tostring(eview)
        for field in res['fields']:
            if 'Hours' in res['fields'][field]['string']:
                res['fields'][field]['string'] = res['fields'][
                    field]['string'].replace('Hours', tm)
        return res

    @api.multi
    def delegate(self):
        self.ensure_one()
        task_id = self.env.context.get('active_id')
        delegate_data = self.read()[0]
        parent_task = self.env['project.task'].browse(task_id)
        delegated_task_id = parent_task.do_delegate(delegate_data)
        action = self.env.ref('project.action_view_task').read()[0]
        task_view_form_id = self.env.ref('project.view_task_form2').id
        task_view_tree_id = self.env.ref('project.view_task_tree2').id
        action['res_id'] = delegated_task_id
        action['view_id'] = task_view_form_id
        action['views'] = [(task_view_form_id, 'form'),
                           (task_view_tree_id, 'tree')]
        action['help'] = False
        return action
