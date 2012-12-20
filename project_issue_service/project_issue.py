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
from datetime import datetime, timedelta
import time


class project_issue(osv.osv):
    _inherit = 'project.issue'
    _columns = {
    #added fields:
        'functional_block_id': fields.many2one('project.functional_block', 'Component', help = "Component (system, module, function) to be adressed"),
        'assigned_to': fields.related('task_id', 'user_id', string = 'Task Assigned to', type="many2one", relation="res.users", store=True, help='This is the current user to whom the related task was assigned'),
        'tasks': fields.one2many('project.task', 'issue_id', 'Related tasks', help="Task history for the issue"),
        'create_uid': fields.many2one('res.users', 'Created by', help = "Person who reported the issue"),
    #modified fields:
        'categ_id': fields.many2one('crm.case.categ', 'Category', required=True, 
            domain="[('object_id.model','=','project.issue')]", #domain="[('object_id.model', '=', 'project.issue'),('parent_id','!=',None)]",
            help="Only categories with a parent will be selectable in the Issues form."),
    }

    def case_open(self, cr, uid, ids, *args):
        """Open Issue preserving the assigned user_id.
        Standard project_issue.case_open() method forces user_id to the current user.
        This is not appropriate in the case where an administrative user is updating issue status.
        With this enhancement, the original user_id is preserved.
        """
        orig = self.read(cr, uid, ids, ['id', 'user_id'])
        res = super(project_issue, self).case_open(cr, uid, ids, *args)
        for rec in orig:
            if rec['user_id'] and rec['user_id'][0]:
                #Write both 'user_id' and 'date_open' to allow Action Rule Triggers to ignore these changes using "... and not vals.get('date_open')"
                self.write(cr, uid, [rec['id']], {'date_open': time.strftime('%Y-%m-%d %H:%M:%S'), 'user_id' : rec['user_id'][0]} )
        return res

    def _validate_tasks_inactive(self, cr, uid, ids):
        """Ensure there are no related active Tasks""" 
        for issue in self.browse(cr, uid, ids):
            for task in issue.tasks:
                if task.state not in ['done', 'cancel']: 
                    raise osv.except_osv(_('Error !'), _('All related tasks should be inactive. Please check Task "%s".' % task.name))

    def case_cancel(self, cr, uid, ids, *args):
        self._validate_tasks_inactive(cr, uid, ids)
        return super(project_issue, self).case_cancel(cr, uid, ids, *args)

    def case_close(self, cr, uid, ids, *args):
        self._validate_tasks_inactive(cr, uid, ids)
        return super(project_issue, self).case_close(cr, uid, ids, *args)

    def onchange_partner_id(self, cr, uid, ids, part, email=False, proj_id=None, context=None):
        """This function returns value of partner address based on partner
        :param ids: List of case IDs
        :param part: Partner's id
        :param email: Partner's email ID
        """
        #the Issue Address is copied from the project's Contact Address
        if  proj_id:
            data = {}
            proj_obj = self.pool.get('project.project').browse(cr, uid, proj_id, context)
            #Copy address from Project
            contact_id = proj_obj.contact_id and proj_obj.contact_id.id or None
            data.update( {'partner_address_id': contact_id} )
            #Copy "reply_to" email from Project, if none already provided
            if not email:
                email = proj_obj.reply_to
                if email:
                    data.update({'email_from': email})
            return {'value': data}
        #else:
        return super(project_issue, self).onchange_partner_id(cr, uid, ids, part, email)        
        
    def on_change_project(self, cr, uid, ids, proj_id=False, context=None):
        """When changing the Issue's Project:
            - the Issue Partner is copied from the project's Partner
            - cascades the change to the Address and e-mail
        """
        if not proj_id:
            return {'value':{}}
        super_res = super(project_issue, self).on_change_project(cr, uid, ids, proj_id, context = context)
        data = super_res.get('value', {})
        #the Issue Partner is copied from the project's Partner
        proj_obj = self.pool.get('project.project').browse(cr, uid, proj_id, context)
        if proj_obj.partner_id:
            data.update( {'partner_id': proj_obj.partner_id.id} )
        #the Issue Address is copied from the project's Contact Address
        #TODO: code repeated in onchange_partner_id(); check if it's really necessary
        contact_id = proj_obj.contact_id and proj_obj.contact_id.id or None
        data.update( {'partner_address_id': contact_id} )
        #cascades the change to the Address and e-mail
        data.update( self.onchange_partner_id(cr, uid, ids, None, proj_id)['value'] )
        return {'value': data}

    def convert_issue_task(self, cr, uid, ids, context=None):
        for bug in self.browse(cr, uid, ids, context=context):
            if bug.task_id:
                new_task_id  = bug.task_id.id
            else:
                #Task,user_id must be current user; otherwise Task Access Rules may stop task.create
                #Task date start defaults to tomorrow 00:00h
                now = datetime.now()
                date_start = datetime( now.year, now.month, now.day, 0) + timedelta(days=+1)
                new_task_id = self.pool.get('project.task').create(cr, uid, {
                    'section_id': bug.section_id.id,
                    'project_id': bug.project_id.id,
                    'partner_id': bug.partner_id.id,
                    'categ_id': bug.categ_id.id,
                    'functional_block_id': bug.functional_block_id.id,
                    'date_deadline': bug.date_deadline,
                    'date_start': date_start, #changed from standard
                    'planned_hours': 1, #added
                    'name': bug.name,
                    'description':bug.description,
                    'issue_id': bug.id, #added
                    'priority': bug.priority,
                    'user_id': uid, #changed
                })
                self.write(cr, uid, [bug.id], {'task_id': new_task_id})
                self.case_open(cr, uid, [bug.id])

        data_obj = self.pool.get('ir.model.data')
        form_id = data_obj.get_object(cr, uid, 'project', 'view_task_form2').id
        tree_id = data_obj.get_object(cr, uid, 'project', 'view_task_tree2').id
        srch_id = data_obj.get_object(cr, uid, 'project', 'view_task_search_form').id
        return  {
            'name': _('Tasks'),
            'view_type': 'form',
            'view_mode': 'form,tree', 
            'res_model': 'project.task',
            'res_id': int(new_task_id),
            'view_id': False,
            'views': [(form_id,'form'),(tree_id,'tree'),(False,'calendar'),(False,'graph')],
            'type': 'ir.actions.act_window',
            'search_view_id': srch_id,
            'nodestroy': True
        }

    def convert_issue_task_tree(self, cr, uid, ids, context=None):
        """Create Task from Issue, without opening it's form"""
        self.convert_issue_task(cr, uid, ids, context=context)
        return True

project_issue()
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: