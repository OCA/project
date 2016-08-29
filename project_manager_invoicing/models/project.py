# -*- coding: utf-8 -*-
#
#    Author: Yannick Vaucher, ported by Denis Leemann
#    Copyright 2015 Camptocamp SA
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
from openerp.osv import orm, fields
from openerp import SUPERUSER_ID

TASK_WATCHERS = [
    'work_ids',
    'remaining_hours',
    'effective_hours',
    'planned_hours',
]
TIMESHEET_WATCHERS = [
    'unit_amount',
    'product_uom_id',
    'account_id',
    'task_id',
    'invoiced_hours'
]


class ProjectTask(orm.Model):
    _inherit = 'project.task'

    def _progress_rate(self, cr, uid, ids, names, arg, context=None):
        # Modification: Calculation is now based on invoiced_hours in
        # place of unit_amount
        """TODO improve code taken for OpenERP"""
        res = {}
        cr.execute("""SELECT task_id, COALESCE(SUM(invoiced_hours),0)
                        FROM account_analytic_line
                      WHERE task_id IN %s
                      GROUP BY task_id""", (tuple(ids),))
        hours = dict(cr.fetchall())
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = {}
            res[task.id]['effective_hours'] = hours.get(task.id, 0.0)
            res[task.id]['total_hours'] = (
                task.remaining_hours or 0.0) + hours.get(task.id, 0.0)
            res[task.id]['delay_hours'] = res[task.id][
                'total_hours'] - task.planned_hours
            res[task.id]['progress'] = 0.0
            if (task.remaining_hours + hours.get(task.id, 0.0)):
                res[task.id]['progress'] = round(
                    min(100.0 * hours.get(task.id, 0.0) /
                        res[task.id]['total_hours'], 99.99), 2)
            if task.state in ('done', 'cancelled'):
                res[task.id]['progress'] = 100.0
        return res

    # TODO TOTEST
    def _store_set_values(self, cr, uid, ids, field_list, context=None):
        # Hack to avoid redefining most of function fields of project.project
        # model. This is mainly due to the fact that orm _store_set_values use
        # direct access to database. So when modify a line the
        # _store_set_values as it uses cursor directly to update tasks
        # project triggers on task are not called
        res = super(ProjectTask, self)._store_set_values(
            cr, uid, ids, field_list, context=context)
        for row in self. browse(cr, SUPERUSER_ID, ids, context=context):
            if row.project_id:
                project = row.project_id
                project.write({'parent_id': project.parent_id.id})
        return res

    # TODO Vérifier avec méthodes de hr_timesheet =>'project_task'
    def _get_hours(self, cr, uid, ids, vals, names, context=None):
        """ Sum timesheet line invoiced hours """
        res = {}
        cr.execute("""SELECT task_id, COALESCE(SUM(invoiced_hours),0)
                        FROM account_analytic_line
                      WHERE task_id IN %s
                      GROUP BY task_id""", (tuple(ids),))
        hours_unit_amount = dict(cr.fetchall())
        for task in self.browse(cr, uid, ids, context=context):
            # sum(l.invoiced_hours for l in task.work_ids)
            invoiced_hours = hours_unit_amount.get(task.id, 0.0)
            remaining_hours = task.planned_hours - invoiced_hours
            res[task.id] = {'invoiced_hours': invoiced_hours,
                            'remaining_hours': remaining_hours,
                            'total_hours': task.planned_hours + invoiced_hours
                            }

        return res

    # OK
    def _get_analytic_line(self, cr, uid, ids, arg, context=None):
        res = []
        aal_obj = self.pool['account.analytic.line']
        for aal in aal_obj.browse(cr, uid, ids, context=context):
            if aal.task_id:
                res.append(aal.task_id.id)
        return res

    _store_hours = {'project.task': (lambda self, cr, uid, ids, c=None: ids,
                                     TASK_WATCHERS, 20),
                    'account.analytic.line': (_get_analytic_line,
                                              TIMESHEET_WATCHERS, 20)
                    }
    _columns = {
        'invoiced_hours': fields.function(
            _progress_rate,
            type='float',
            store=_store_hours,
            multi="progress"
        ),
        'effective_hours': fields.function(
            _progress_rate, multi="progress", string='Time Spent',
            help="Computed using the sum of the task work done (timesheet "
                 "lines associated on this task).",
            store={'project.task': (lambda self, cr, uid, ids, c=None: ids,
                                    TASK_WATCHERS, 20),
                   'account.analytic.line': (_get_analytic_line,
                                             TIMESHEET_WATCHERS, 20)}),
        'delay_hours': fields.function(
            _progress_rate, multi="progress", string='Deduced Hours',
            help="Computed as difference between planned hours by the project "
                 "manager and the total hours of the task.",
            store={'project.task': (lambda self, cr, uid, ids, c=None: ids,
                                    TASK_WATCHERS, 20),
                   'account.analytic.line': (_get_analytic_line,
                                             TIMESHEET_WATCHERS, 20)}),
        'total_hours': fields.function(
            _progress_rate, multi="progress", string='Total Time',
            help="Computed as: Time Spent + Remaining Time.",
            store={'project.task': (lambda self, cr, uid, ids, c=None: ids,
                                    TASK_WATCHERS, 20),
                   'account.analytic.line': (_get_analytic_line,
                                             TIMESHEET_WATCHERS, 20)}),
        'progress': fields.function(
            _progress_rate, multi="progress", string='Progress', type='float',
            group_operator="avg",
            help="If the task has a progress of 99.99% you should close the "
                 "task if it's finished or reevaluate the time",
            store={'project.task': (lambda self, cr, uid, ids, c=None: ids,
                                    TASK_WATCHERS, 20),
                   'account.analytic.line': (_get_analytic_line,
                                             TIMESHEET_WATCHERS, 20)})
        # 'remaining_hours': fields.function(
        #     _get_hours,
        #     type='float',
        #     store=_store_hours,
        #     multi="progress"
        # ),
    }
