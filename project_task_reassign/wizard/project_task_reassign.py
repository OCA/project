# -*- coding: utf-8 -*-
##############################################################################
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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class project_task_reassign(osv.TransientModel):
    _name = 'project.task.reassign'
    _description = 'Task Reassign'

    _columns = {
        'project_id': fields.many2one(
            'project.project', 'Project',
            help="Project this task should belong to"),
        'user_id': fields.many2one(
            'res.users', 'Assign To',
            help="User you want to assign this task to"),
        }

    def reassign(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        task_ids = context.get('active_ids') or [context.get('active_id')]
        assert task_ids, _("No active Tasks found.")
        assign_to = self.browse(cr, uid, ids, context=context)[0]
        return self.pool.get('project.task').do_reassign(
            cr, uid, task_ids,
            assign_to.user_id and assign_to.user_id.id or None,
            assign_to.project_id and assign_to.project_id.id or None,
            context=context)
