# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Daniel Reis
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
from osv import fields, osv
from tools.translate import _

class project_task_reevaluate(osv.osv_memory):
    _inherit = 'project.task.reevaluate'

    def compute_hours(self, cr, uid, ids, context=None):
        """
        Reevaluate relinks the Issue's current Task
        """
        task_pool  = self.pool.get('project.task')
        issue_pool = self.pool.get('project.issue')
        for o in task_pool.browse(cr, uid, context.get('active_ids', list()), context=context):
            if o.issue_id and not o.issue_id.task_id:
                issue_pool.write(cr, uid, [o.issue_id.id], {'task_id': o.id}, context=context)  
        return super(project_task_reevaluate, self).compute_hours(cr, uid, ids, context)
project_task_reevaluate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
