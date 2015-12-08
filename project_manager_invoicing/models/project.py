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
from openerp.tools.translate import _

TASK_WATCHERS = [
    'work_ids',
    'remaining_hours',
    'effective_hours',
    'planned_hours'
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
    _name = 'project.task'

    #TOTEST
    def _progress_rate(self, cr, uid, ids, names, arg, context=None):
        """ OVERWRITE _progress_rate to make calculation with invoiced_hours
        and not unit_amount & added calculation of new fields"""
        """TODO improve code taken for OpenERP"""  #Comment already there
        import pdb; pdb.set_trace()
        res = {}
        """ invoiced_hours in place of unit_amount """
        cr.execute("""SELECT task_id, COALESCE(SUM(invoiced_hours),0) 
                        FROM account_analytic_line
                      WHERE task_id IN %s
                      GROUP BY task_id""", (tuple(ids),))
        hours = dict(cr.fetchall())
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = {}
            res[task.id]['invoiced_hours'] = hours.get(task_id, 0.0)
            res[task.id]['remaining_hours'] = task.planned_hours - hours.get(task_id, 0.0)
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

    #TODO Vérifier avec méthodes de hr_timesheet =>'project_task'
    def _get_hours(self, cr, uid, ids, vals, names, context=None):
        """ Sum timesheet line invoiced hours """
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            invoiced_hours = sum(l.invoiced_hours for l in task.work_ids)
            res[task.id] = {'invoiced_hours': invoiced_hours,
                            'remaining_hours': task.planned_hours - invoiced_hours}
        return res

    # OK
    def _get_analytic_line(self, cr, uid, ids, arg, context=None):
        res = []
        for aal in self.pool['account.analytic.line'].browse(cr, uid, ids, context=context):
            if aal.task_id:
                res.append(aal.task_id.id)
        return res

    _store_hours = {'project.task': (lambda self, cr, uid, ids, c={}: ids,
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
        'remaining_hours': fields.function(
            _progress_rate,
            type='float',
            store=_store_hours,
            multi="progress"
        ),
    }
