# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
import operator

from lxml import etree

from openerp import models, fields, api, _,tools


class PlustronProject(models.Model):
    _inherit = 'project.task'

    task_count_delegate = fields.Integer(
        compute="_compute_task_count",
        store=True,
        string="Task Delegate")

    @api.one
    @api.depends('parent_ids')
    def _compute_task_count(self):
        self.task_count_delegate = len(self.parent_ids)

    def _check_child_task(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        tasks = self.browse(cr, uid, ids, context=context)
        for task in tasks:
            if task.child_ids:
                for child in task.child_ids:
                    if child.stage_id and not child.stage_id.fold:
                        raise UserWarning(_("Warning!"),
                                          _("Child task still open.\nPlease cancel or complete child task first."))
        return True

    @api.one
    def _delegate_task_attachments(self, delegated_task_id):
        attachment = self.env['ir.attachment']
        attachments = attachment.search(
            [('res_model', '=', self._name), ('res_id', '=', self.browse(self._context.get('active_ids', False)).id)])
        new_attachment_ids = []
        for attachment in attachments:
            new_attachment_ids.append(
                attachment.copy(default={'res_id': delegated_task_id.id}))
        return new_attachment_ids

    @api.multi
    def do_delegate(self, delegate_data=None):
        delegated_tasks = {}
        for task in self.browse(self._context.get('active_ids', False)):
            delegated_task_id = task.copy({
                'name': delegate_data['name'],
                'project_id': delegate_data['project_id'] and delegate_data['project_id'][0] or False,
                'stage_id': min(task.project_id.type_ids, key=operator.itemgetter('sequence')).id,
                'user_id': delegate_data['user_id'] and delegate_data['user_id'][0] or False,
                'planned_hours': delegate_data['planned_hours'] or 0.0,
                'parent_ids': [(6, 0, [task.id])],
                'description': delegate_data['new_task_description'] or '',
                'child_ids': [],
                'timesheet_ids': []
            })
            self._delegate_task_attachments(delegated_task_id)
            newname = delegate_data['prefix'] or ''
            task.write({
                'remaining_hours': delegate_data['planned_hours_me'],
                'planned_hours': delegate_data['planned_hours_me'] + (task.effective_hours or 0.0),
                'name': newname,
            })
            delegated_tasks[task.id] = delegated_task_id
        return delegated_tasks


class PlustronProjectTaskDelegate(models.TransientModel):
    _name = 'project.task.delegate'
    _description = 'Task Delegate'

    name = fields.Char('Delegated Title', required=True, help="New title of the task delegated to the user")
    prefix = fields.Char('Your Task Title', help="Title for your validation task")
    project_id = fields.Many2one('project.project', 'Project', help="User you want to delegate this task to")
    user_id = fields.Many2one('res.users', 'Assign To', required=True, help="User you want to delegate this task to")
    new_task_description = fields.Text('New Task Description',
                                       help="Reinclude the description of the task in the task of the user",
                                       widget="html")
    planned_hours = fields.Float('Planned Hours', help="Estimated time to close this task by the delegated user",
                                 default=1.0)
    planned_hours_me = fields.Float('Hours to Validate',
                                    help="Estimated time for you to validate the work done by the user to whom you delegate this task")
    state = fields.Selection([('pending', 'Pending'), ('done', 'Done'), ], 'Validation State', default="pending",
                             help="New state of your own task. Pending will be reopened automatically when the delegated task is closed")

    @api.multi
    def onchange_project_id(self, project_id=False):
        project_project = self.env['project.project']
        if not project_id:
            return {'value': {'user_id': False}}
        project = project_project.browse(project_id)
        return {'value': {'user_id': project.user_id and project.user_id.id or False}}

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(PlustronProjectTaskDelegate, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res
        task_pool = self.pool.get('project.task')
        task = task_pool.browse(cr, uid, record_id, context=context)
        task_name = tools.ustr(task.name)

        if 'project_id' in fields:
            res['project_id'] = int(task.project_id.id) if task.project_id else False

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

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(PlustronProjectTaskDelegate, self).fields_view_get(cr, uid, view_id, view_type, context=context,
                                                                       toolbar=toolbar, submenu=submenu)
        users_pool = self.pool.get('res.users')
        obj_tm = users_pool.browse(cr, uid, uid, context=context).company_id.project_time_mode_id
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
                res['fields'][field]['string'] = res['fields'][field]['string'].replace('Hours', tm)
        return res

    @api.multi
    def delegate(self):
        task_id = self._context.get('active_id', False)
        task_pool = self.env['project.task']
        delegate_data = self.read()[0]
        delegated_tasks = task_pool.do_delegate(delegate_data)
        action = self.env.ref('project.action_view_task')
        view_task_form = self.env.ref('project.view_task_form2')
        view_task_tree = self.env.ref('project.view_task_tree2')
        action['res_id'] = delegated_tasks[task_id]
        action['view_id'] = False
        action['views'] = [(view_task_form.id, 'form'), (view_task_tree.id, 'tree')]
        action['help'] = False
        return action
