# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Buron. Copyright Yannick Buron
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


class ProjectTaskType(orm.Model):

    """
    Specify the default assigned partner for each stage,
    and trigger config update on each project when changed
    """
    _inherit = 'project.task.type'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Assigned partner'),
    }

    def _boolean_update_projects(self, cr, uid, vals, context=None):
        # Check if we should update projects
        res = False
        if 'partner_id' in vals:
            res = True
        return res

    def _update_assigned_partner(self, cr, uid, ids, vals, context=None):
        # Update config in project
        project_obj = self.pool.get('project.project')
        if self._boolean_update_projects(cr, uid, vals, context=context):
            project_ids = {}
            for type in self.browse(cr, uid, ids, context=context):
                for project in type.project_ids:
                    project_ids[project.id] = project.id
            project_obj._update_stored_config(
                cr, uid, list(project_ids), context=context
            )

    def create(self, cr, uid, vals, context=None):
        # Trigger update config on create
        res = super(ProjectTaskType, self).create(
            cr, uid, vals, context=context
        )
        self._update_assigned_partner(cr, uid, [res], vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        # Trigger update config on write
        res = super(ProjectTaskType, self).write(
            cr, uid, ids, vals, context=context
        )
        self._update_assigned_partner(cr, uid, ids, vals, context=context)
        return res
