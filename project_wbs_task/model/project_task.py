# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#               <contact@eficent.com>
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

from openerp.osv import fields, orm


class task(orm.Model):
    _inherit = 'project.task'

    def _project_complete_wbs_name(self, cr, uid, ids, prop, unknow_none, context=None):
        if not ids:
            return []

        res = []

        data_project = []

        project_obj = self.pool.get('project.project')

        tasks = self.browse(cr, uid, ids, context=None)

        for task in tasks:
            if task.project_id:
                task_project_id = task.project_id.id
                data_project = project_obj.read(cr, uid, task_project_id,
                                                ['complete_wbs_name'],
                                                context=context)
            if data_project:
                res.append((task.id, data_project['complete_wbs_name']))
            else:
                res.append((task.id, ''))
        return dict(res)

    def _project_complete_wbs_code(self, cr, uid, ids, prop, unknow_none,
                                   context=None):

        if not ids:
            return []

        res = []
        data_project = []

        project_obj = self.pool.get('project.project')

        tasks = self.browse(cr, uid, ids, context=None)

        for task in tasks:
            if task.project_id:
                task_project_id = task.project_id.id
                data_project = project_obj.read(cr, uid, task_project_id,
                                                ['complete_wbs_code'],
                                                context=context)
            if data_project:
                res.append((task.id, data_project['complete_wbs_code']))
            else:
                res.append((task.id, ''))
        return dict(res)

    _columns = {
        'analytic_account_id': fields.related(
            'project_id', 'analytic_account_id',
            type='many2one',
            relation='account.analytic.account',
            string='Analytic Account', store=True, readonly=True),

        'project_complete_wbs_code': fields.related(
            'analytic_account_id', 'complete_wbs_code',
            type='char', size=250, string='Full WBS Code', readonly=True),
        'project_complete_wbs_name': fields.related(
            'analytic_account_id', 'complete_wbs_name',
            type='char', size=250, string='Full WBS Name', readonly=True),
        }
