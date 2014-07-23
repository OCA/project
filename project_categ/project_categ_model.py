# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Daniel Reis
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


class ProjectProject(orm.Model):
    _inherit = 'project.project'
    _columns = {
        'task_categ_id': fields.many2one(
            'project.category', 'Root Category for Tasks'),
        }


class ProjectCategory(orm.Model):
    _inherit = 'project.category'

    def _name_get(self, cr, uid, ids, context=None):
        res = []
        rows = self.read(cr, uid, ids, ['name', 'parent_id'], context=context)
        for row in rows:
            parent = row['parent_id'] and (row['parent_id'][1] + ' / ') or ''
            res.append((row['id'], parent + row['name']))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        return dict(self._name_get(cr, uid, ids, context=context))

    _columns = {
        'parent_id': fields.many2one(
            'project.category', 'Parent Category', select=True),
        'child_ids': fields.one2many(
            'project.category', 'parent_id', 'Child Categories'),
        'complete_name': fields.function(
            _name_get_fnc, method=True, type='char', string='Name'),
        'code': fields.char('Code', size=10),
    }
    _order = 'parent_id,name'


class ProjectTask(orm.Model):
    _inherit = 'project.task'

    def onchange_project(self, cr, uid, id, project_id, context=None):
        # on_change is necessary to populate fields on create, before saving
        try:
            res = super(ProjectTask, self).onchange_project(
                cr, uid, id, project_id, context) or {}
        except AttributeError:
            res = {}

        if project_id:
            obj = self.pool.get('project.project').browse(
                cr, uid, project_id, context=context)
            if obj.task_categ_id:
                res.setdefault('value', {})
                res['value']['task_categ_id'] = obj.task_categ_id.id
        return res

    _columns = {
        'task_categ_id': fields.related(
            'project_id', 'task_categ_id', string="Category Root",
            type='many2one', relation='project.category', readonly=True),
        'categ_ids': fields.many2many(
            'project.category', string='Tags',
            domain="[('id','child_of',task_categ_id)"
                   ",('id','!=',task_categ_id)]"),
    }
