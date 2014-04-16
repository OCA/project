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


class project_action_item(orm.Model):
    _name = "project.action.item"
    _description = "Project Action Items"

    _columns = {
        'task_id': fields.many2one('project.task', 'Related Task'),
        'name': fields.char('Description', size=256, required=True),
        'date_deadline': fields.date('Deadline'),
        'date_done': fields.date('Date Done'),
        'user_id': fields.many2one('res.users', 'Assigned To'),
        'estimated_quantity': fields.float('Estimated Quantity'),
        'timesheet_ids': fields.one2many(
            'hr.analytic.timesheet', 'action_item_id', 'Related Timesheets'),
        'state': fields.selection([
            ('todo', 'To Do'),
            ('done', 'Done'),
            ], 'State', readonly=True),
        'create_uid': fields.many2one(
            'res.users', 'Created By', readonly=True),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'sequence': fields.integer('Sequence'),
        }

    _defaults = {
        'state': 'todo',
        }

    def set_to_done(self, cr, uid, ids, context=None):
        today = fields.date.context_today(self, cr, uid, context=context)
        self.write(cr, uid, ids, {
            'state': 'done',
            'date_done': today,
            }, context=context)
        return

    def back_to_todo(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'todo',
            'date_done': False,
            }, context=context)
        return


class hr_analytic_timesheet(orm.Model):
    _inherit = "hr.analytic.timesheet"

    _columns = {
        'action_item_id': fields.many2one(
            'project.action.item', 'Action Item'),
        }


class project_task(orm.Model):
    _inherit = "project.task"

    _columns = {
        'todo_action_item_ids': fields.one2many(
            'project.action.item', 'task_id', 'Action Items To Do',
            domain=[('state', '=', 'todo')]),
        'done_action_item_ids': fields.one2many(
            'project.action.item', 'task_id', 'Action Items Done',
            domain=[('state', '=', 'done')]),
        'action_item_ids': fields.one2many(
            'project.action.item', 'task_id', 'Action Items'),
        }
