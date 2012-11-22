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

from crm import crm
from osv import fields, osv
from datetime import datetime, timedelta

###TASK_TYPE_USE_GROUPS = [('resolution', 'Resolution Stage'), ('cause', 'Problem Cause')]

#class project_task_type(osv.osv):
#    _inherit = 'project.task.type'
#    _sort = 'use_group, sequence'
#    _columns = {
#        'use_group': fields.selection( TASK_TYPE_USE_GROUPS , 'Usage', size=16),
#        'code': fields.char('Code', size=10),
#    }
#project_task_type()


#class project_functional_block(osv.osv):
#    _inherit = 'project.functional_block'
#    _columns = {
#        'code': fields.char('Code', size=10),
#    }
#project_functional_block()

class task(osv.osv):
    _inherit = "project.task"
    _columns = {
        #modified fields:
        'section_id': fields.many2one('crm.case.section', 'Service Team', select=True,\
            help='Service team to which Task belongs to.'), #standard: relabeled
        'priority': fields.selection(crm.AVAILABLE_PRIORITIES, 'Priority', select=True), #Standard is 0-4; changed to conform with project_issue (1-5)!
        #added fields:
        'issue_id': fields.many2one('project.issue', 'Related Issue', readonly=True, 
            help="Issue related to this task"),
        'categ_id': fields.related('issue_id', 'categ_id', string='Issue Category', type="many2one", relation='crm.case.categ', store=True),
    }
        
    def do_close(self, cr, uid, ids, context=None):
        """
        Clean up related Issues's 'Current Task', and set issue state to either
        'done' or 'pending', if pending work is described in the 'todo_desc' field.
        """
        #Tasks must be closed first, because Issues with active tasks can't be closed
        res = super(task, self).do_close(cr, uid, ids, context)
        #Update related issue state
        issue_model = self.pool.get('project.issue')
        for tsk in self.browse(cr, uid, ids):
            if tsk.issue_id and tsk.issue_id.state not in ['done', 'cancel']:
                #Current task cleaned up, so that the "Create Task" button is shown again
                issue_model.write(cr, uid, [tsk.issue_id.id], {'task_id': None}, context=context)
                #If pending work, issue is not closed, but set to "PENDING"
                if tsk.todo_desc:
                    issue_model.case_pending(cr, uid, [tsk.issue_id.id])
                else:
                    issue_model.case_close(cr, uid, [tsk.issue_id.id])
        return res
   
    def do_cancel(self, cr, uid, ids, context=None):
        """
        Clean up related Issues's 'Current Task'
        """ 
        issue_model = self.pool.get('project.issue')
        for tsk in self.browse(cr, uid, ids):
            if tsk.issue_id and tsk.issue_id.state not in ['closed', 'cancelled']:
                issue_model.write(cr, uid, [tsk.issue_id.id], {'task_id': None}, context=context)
        return super(task, self).do_cancel(cr, uid, ids, context)

task()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


