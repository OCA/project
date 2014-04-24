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


class project_action_item_timesheet(orm.TransientModel):
    _name = 'project.action.item.timesheet'
    _description = 'Update Action Item and Create Timesheet Line'

    _columns = {
        'date': fields.date('Date', required=True),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'hours': fields.float('Worked Hours'),
        'name': fields.char('Work Description', size=256, required=True),
        'to_invoice': fields.many2one(
            'hr_timesheet_invoice.factor', 'Timesheet Invoicing Ratio'),
        'completed': fields.boolean('Action Item Completed'),
        }

    def default_get(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        active_id = context.get('active_id')
        res = {}
        if active_id:
            item = self.pool['project.action.item'].browse(
                cr, uid, active_id, context=context)
            if not item.task_id:
                raise orm.except_orm(
                    _('Error:'),
                    _("This action item is not linked to a task, "
                        "so we cannot generate a timesheet from it."))
            remaining = item.estimated_hours - item.timesheet_hours
            if remaining < 0:
                remaining = 0
            res = {
                'name': item.name,
                'quantity': remaining,
                'to_invoice': item.to_invoice.id or False,
            }
        res.update({
            'user_id': uid,
            'date': fields.date.context_today(self, cr, uid, context=context),
            'completed': context.get('action_item_completed'),
            })
        return res

    def _prepare_timesheet(self, cr, uid, action_item, wizard, context=None):
        task_id = action_item.task_id.id
        to_invoice = wizard.to_invoice.id or False
        res_user = self.pool['hr.analytic.timesheet'].on_change_user_id(
            cr, uid, False, context['user_id'])
        journal_id = res_user['value']['journal_id']
        product_id = res_user['value']['product_id']
        res_unit = self.pool['hr.analytic.timesheet'].on_change_unit_amount(
            cr, uid, False, product_id, wizard.hours, False, unit=False,
            journal_id=journal_id, task_id=task_id, to_invoice=to_invoice,
            context=context)
        res_unit['value'].update({
            'name': wizard.name,
            'date': wizard.date,
            'user_id': wizard.user_id.id,
            'unit_amount': wizard.hours,
            'journal_id': journal_id,
            'task_id': task_id,
            'to_invoice': to_invoice,
            'action_item_id': action_item.id,
            })
        return res_unit['value']

    def _prepare_action_item_update(
            self, cr, uid, action_item, wizard, context=None):
        if wizard.completed:
            res = {
                'state': 'done',
                'date_done': wizard.date,
                }
        else:
            res = {'state': 'progress'}
        return res

    def update_action_create_timesheet(self, cr, uid, ids, context=None):
        assert len(ids) == 1, "Only one ID"
        wizard = self.browse(cr, uid, ids[0], context=context)
        if context is None:
            context = {}
        action_item_id = context['active_id']
        ts_ctx = context.copy()
        ts_ctx['user_id'] = wizard.user_id.id
        action_item_obj = self.pool['project.action.item']
        action_item = action_item_obj.browse(
            cr, uid, action_item_id, context=context)
        ts_vals = self._prepare_timesheet(
            cr, uid, action_item, wizard, context=ts_ctx)
        self.pool['hr.analytic.timesheet'].create(
            cr, uid, ts_vals, context=ts_ctx)
        action_vals = self._prepare_action_item_update(
            cr, uid, action_item, wizard, context=context)
        self.pool['project.action.item'].write(
            cr, uid, action_item_id, action_vals, context=context)
        if context.get('project_action_item_main_view'):
            res = True
        else:
            # refresh the view of the task after completion of the wizard
            res = {
                'name': _('Task'),
                'type': 'ir.actions.act_window',
                'res_model': 'project.task',
                'view_type': 'form',
                'view_mode': 'form,tree,kanban,calendar,gantt,graph',
                'nodestroy': False,
                'target': 'current',
                'res_id': action_item.task_id.id,
                'context': context,
                }
        return res
