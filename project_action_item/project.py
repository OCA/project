# -*- encoding: utf-8 -*-
##############################################################################
#
#    Project Action Item module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class project_action_item(orm.Model):
    _name = "project.action.item"
    _description = "Project Action Items"

    def _compute_timesheet_hours(
            self, cr, uid, ids, name, arg, context=None):
        res = {}
        for action in self.browse(cr, uid, ids, context=context):
            res[action.id] = 0
            for timesheet in action.timesheet_ids:
                res[action.id] += timesheet.unit_amount
        return res

    def _get_action_from_timesheet(self, cr, uid, ids, context=None):
        return self.pool['project.action.item'].search(
            cr, uid, [('timesheet_ids', 'in', ids)], context=context)

    _columns = {
        'task_id': fields.many2one('project.task', 'Related Task'),
        'name': fields.char('Description', size=256, required=True),
        'date_deadline': fields.date('Deadline'),
        'date_done': fields.date('Date Done'),
        'user_id': fields.many2one('res.users', 'Assigned To'),
        'estimated_hours': fields.float('Estimated Hours'),
        'to_invoice': fields.many2one(
            'hr_timesheet_invoice.factor', 'Expected Invoicing Ratio'),
        'timesheet_ids': fields.one2many(
            'hr.analytic.timesheet', 'action_item_id', 'Related Timesheets'),
        'timesheet_hours': fields.function(
            _compute_timesheet_hours, type='float',
            string="Worked Hours", readonly=True, store={
                'hr.analytic.timesheet': (
                    _get_action_from_timesheet,
                    ['unit_amount', 'action_item_id'],
                    10),
                }, help="This is the sum of the related timesheets."
            ),
        'state': fields.selection([
            ('todo', 'To Do'),
            ('progress', 'In Progress'),
            ('done', 'Done'),
            ], 'State', readonly=True),
        'create_uid': fields.many2one(
            'res.users', 'Created By', readonly=True),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'sequence': fields.integer('Sequence'),
        }

    def _get_default_invoice_ratio(self, cr, uid, context=None):
        if context is None:
            context = {}
        active_id = context.get('active_id')
        active_model = context.get('active_model')
        if active_model == 'project.task' and active_id:
            task = self.pool['project.task'].browse(
                cr, uid, active_id, context=context)
            return task.project_id and task.project_id.to_invoice.id or False
        else:
            return False

    _defaults = {
        'state': 'todo',
        'to_invoice': _get_default_invoice_ratio,
        }

    def set_to_done(self, cr, uid, ids, context=None):
        today = fields.date.context_today(self, cr, uid, context=context)
        self.write(cr, uid, ids, {
            'state': 'done',
            'date_done': today,
            }, context=context)
        return

    def set_to_progress(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'progress',
            }, context=context)
        return

    def back_to_todo(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'todo',
            'date_done': False,
            }, context=context)
        return

    def action_item_done_with_timesheet_wizard(
            self, cr, uid, ids, context=None):
        # I cannot pass the context is the button of a tree view,
        # that's why I wrote a special function for that...
        if context is None:
            context = {}
        context['action_item_completed'] = True
        return {
            'name': _('Update Action Item and Create Timesheet Line'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.action.item.timesheet',
            'view_type': 'form',
            'view_mode': 'form',
            'nodestroy': True,
            'target': 'new',
            'context': context,
        }


class hr_analytic_timesheet(orm.Model):
    _inherit = "hr.analytic.timesheet"

    _columns = {
        'action_item_id': fields.many2one(
            'project.action.item', 'Action Item'),
        }


class project_task(orm.Model):
    _inherit = "project.task"

    def _compute_planned_hours(
            self, cr, uid, ids, name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = 0
            for action in task.action_item_ids:
                res[task.id] += action.estimated_hours
        return res

    def _get_task_from_action(self, cr, uid, ids, context=None):
        return self.pool['project.task'].search(
            cr, uid, [('action_item_ids', 'in', ids)], context=context)

    _columns = {
        'to_work_action_item_ids': fields.one2many(
            'project.action.item', 'task_id', 'Action Items To Do',
            domain=[('state', 'in', ('todo', 'progress'))]),
        'done_action_item_ids': fields.one2many(
            'project.action.item', 'task_id', 'Action Items Done',
            domain=[('state', '=', 'done')]),
        'action_item_ids': fields.one2many(
            'project.action.item', 'task_id', 'Action Items'),
        'planned_hours': fields.function(
            _compute_planned_hours, type="float",
            string="Initially Planned Hours", store={
                'project.action.item': (
                    _get_task_from_action,
                    ['estimated_hours', 'task_id'],
                    10),
                },
            help="Estimated time to do the task. It is the sum of the "
            "estimated time of all the action items of this task."),
        }
