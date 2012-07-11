# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis, 2011
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

import crm
from osv import fields, osv
from tools.translate import _
from datetime import datetime, timedelta
import time

class crm_case_section(osv.osv):
    _inherit = "crm.case.section"
    _columns = {
        'resource_calendar_id' : fields.many2one('resource.calendar', 'Working Time',\
            help="Timetable working hours to calculate issue open time", ),
    }
crm_case_section()
    
    
#----------------------------------------------------------
# Project Issue
#
#   * Field to assign Code (.ref), using a "project.issue" sequence
#   * On change of project_id, get the corresponding partner, address and email
#
#----------------------------------------------------------
class project_issue(osv.osv):
    _inherit = 'project.issue'

##TODO: needs further fixing?
#    #FIXED, based on 6.1 trunk @ 2012-02-06
#    #Allow optional project_id and project_id.resource_id
#    def _compute_day(self, cr, uid, ids, fields, args, context=None):
#        """
#        @param cr: the current row, from the database cursor,
#        @param uid: the current user’s ID for security checks,
#        @param ids: List of Openday’s IDs
#        @return: difference between current date and log date
#        @param context: A standard dictionary for contextual values
#        """
#        ###rint '=== PATCHED', ids, fields, '==='
#        cal_obj = self.pool.get('resource.calendar')
#        res_obj = self.pool.get('resource.resource')
#
#        res = {}
#        for issue in self.browse(cr, uid, ids, context=context):
#            #reis:  replaced "issue.project_id.resource_calendar_id" by var "rescal"
#            #       rest of the code is unchanged
#            rescal = None
#            if issue.project_id and issue.project_id.resource_calendar_id:
#                rescal = issue.project_id.resource_calendar_id.id
#            elif issue.section_id and issue.section_id.resource_calendar_id:
#                rescal = issue.section_id.resource_calendar_id.id
#            #reiS: end                
#                
#            for field in fields:
#                res[issue.id] = {}
#                duration = 0
#                ans = False
#                hours = 0
#
#                date_create = datetime.strptime(issue.create_date, "%Y-%m-%d %H:%M:%S")
#                if field in ['working_hours_open','day_open']:
#                    if issue.date_open:
#                        date_open = datetime.strptime(issue.date_open, "%Y-%m-%d %H:%M:%S")
#                        ans = date_open - date_create
#                        date_until = issue.date_open
#                        #Calculating no. of working hours to open the issue
#                        hours = cal_obj.interval_hours_get(cr, uid, rescal, ###reis
#                                                           date_create,
#                                                           date_open)
#                elif field in ['working_hours_close','day_close']:
#                    if issue.date_closed:
#                        date_create = datetime.strptime(issue.create_date, "%Y-%m-%d %H:%M:%S")
#                        date_close = datetime.strptime(issue.date_closed, "%Y-%m-%d %H:%M:%S")
#                        date_until = issue.date_closed
#                        ans = date_close - date_create
#                        #Calculating no. of working hours to close the issue
#                        hours = cal_obj.interval_hours_get(cr, uid, rescal, ###reis
#                               date_create,
#                               date_close)
#                elif field in ['days_since_creation']:
#                    if issue.create_date:
#                        days_since_creation = datetime.today() - datetime.strptime(issue.create_date, "%Y-%m-%d %H:%M:%S")
#                        res[issue.id][field] = days_since_creation.days
#                    continue
#
#                elif field in ['inactivity_days']:
#                    res[issue.id][field] = 0
#                    if issue.date_action_last:
#                        inactive_days = datetime.today() - datetime.strptime(issue.date_action_last, '%Y-%m-%d %H:%M:%S')
#                        res[issue.id][field] = inactive_days.days
#                    continue
#
#                if ans:
#                    resource_id = False
#                    if issue.user_id:
#                        resource_ids = res_obj.search(cr, uid, [('user_id','=',issue.user_id.id)])
#                        if resource_ids and len(resource_ids):
#                            resource_id = resource_ids[0]
#                    duration = float(ans.days)
#                    if rescal: ###reis; issue.project_id and issue.project_id.resource_calendar_id:
#                        duration = float(ans.days) * 24
#
#                        new_dates = cal_obj.interval_min_get(cr, uid,
#                                                             rescal, ###reis; issue.project_id.resource_calendar_id.id,
#                                                             date_create,
#                                                             duration, resource=resource_id)
#                        no_days = []
#                        date_until = datetime.strptime(date_until, '%Y-%m-%d %H:%M:%S')
#                        for in_time, out_time in new_dates:
#                            if in_time.date not in no_days:
#                                no_days.append(in_time.date)
#                            if out_time > date_until:
#                                break
#                        duration = len(no_days)
#                if field in ['working_hours_open','working_hours_close']:
#                    res[issue.id][field] = hours
#                else:
#                    res[issue.id][field] = abs(float(duration))
#        return res

    _columns = {
    #standard fields (changing texts or domains):
        'functional_block_id': fields.many2one('project.functional_block', 'Component', help = "Component (system, module, function) to be adressed"),
    #added fields:
        'assigned_to': fields.related('task_id', 'user_id', string = 'Task Assigned to', type="many2one", relation="res.users", store=True, help='This is the current user to whom the related task was assigned'),
        'ref': fields.char('Code', size=10, readonly=True, select=True, help="Issue sequence number"),
        'tasks': fields.one2many('project.task', 'issue_id', 'Related tasks', help="Task history for the issue"),
        'create_uid': fields.many2one('res.users', 'Created by', help = "Person who reported the issue"),
#TODO:
#        #No changes, repeated to force link to new version of _compute_day()
#        'days_since_creation': fields.function(_compute_day, string='Days since creation date', \
#                                               multi='compute_day', type="integer", help="Difference in days between creation date and current date"),
#        'day_open': fields.function(_compute_day, string='Days to Open', \
#                                multi='compute_day', type="float", store=True),
#        'day_close': fields.function(_compute_day, string='Days to Close', \
#                                multi='compute_day', type="float", store=True),
#        'working_hours_open': fields.function(_compute_day, string='Working Hours to Open the Issue', \
#                                multi='compute_day', type="float", store=True),
#        'working_hours_close': fields.function(_compute_day, string='Working Hours to Close the Issue', \
#                                multi='compute_day', type="float", store=True),
#        'inactivity_days': fields.function(_compute_day, string='Days since last action', \
#                                multi='compute_day', type="integer", help="Difference in days between last action and current date"),
    }
    
    def create(self, cr, uid, vals, context={}):
        vals['ref'] = self.pool.get('ir.sequence').next_by_code(cr, uid, 'project.issue')
        return super(project_issue, self).create(cr, uid, vals, context)        

    def case_open(self, cr, uid, ids, *args):
        """Open Issue preserving the assigned user_id.
        
        Standard project_issue.case_open() method forces user_id to the current user.
        This is not appropriate in the case where am administrative user is updating issue status.
        With this enhancement, the original user_id is preserved.
        """
        orig = self.read(cr, uid, ids, ['id', 'user_id'])
        res = super(project_issue, self).case_open(cr, uid, ids, *args)
        for rec in orig:
            if rec['user_id'] and rec['user_id'][0]:
                #Write both 'user_id' and 'date_open' to allow Action Rule Triggers to ignore these changes using "... and not vals.get('date_open')"
                print {'date_open': time.strftime('%Y-%m-%d %H:%M:%S'), 'user_id' : rec['user_id'][0]} ###
                self.write(cr, uid, [rec['id']], {'date_open': time.strftime('%Y-%m-%d %H:%M:%S'), 'user_id' : rec['user_id'][0]} )
        return res

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

    #copied from project_issue model;
    #changes are marked with "dreis"
    def convert_issue_task(self, cr, uid, ids, context=None):
        case_obj = self.pool.get('project.issue')
        data_obj = self.pool.get('ir.model.data')
        task_obj = self.pool.get('project.task')

        if context is None:
            context = {}

        result = data_obj._get_id(cr, uid, 'project', 'view_task_search_form')
        res = data_obj.read(cr, uid, result, ['res_id'])
        id2 = data_obj._get_id(cr, uid, 'project', 'view_task_form2')
        id3 = data_obj._get_id(cr, uid, 'project', 'view_task_tree2')
        if id2:
            id2 = data_obj.browse(cr, uid, id2, context=context).res_id
        if id3:
            id3 = data_obj.browse(cr, uid, id3, context=context).res_id

        for bug in case_obj.browse(cr, uid, ids, context=context):
            #Only create new task if none is assigned, or if it's done/cancelled
            if bug.task_id.id and bug.task_id.state not in ['cancelled', 'done']:
                new_task_id  = bug.task_id.id
            else:
                #Task,user_id must be current user; otherwise Task Access Rules may stop task.create
                #Task date start defaults to tomorrow 00:00h
                now = datetime.now()
                date_start = datetime( now.year, now.month, now.day, 0) + timedelta(days=+1)
                new_task_id = task_obj.create(cr, uid, {
                    'section_id': bug.section_id.id,
                    'project_id': bug.project_id.id,
                    'partner_id': bug.partner_id.id,
                    'categ_id': bug.categ_id.id,
                    'functional_block_id': bug.functional_block_id.id,
                    'date_deadline': bug.date_deadline,
                    'date_start': date_start, #changed from standard
                    'planned_hours': 1, #added to standard
                    'name': bug.name,
                    'description':bug.description,
                    'issue_id': bug.id, #added
                    'priority': bug.priority,
                    'user_id': uid, #changed
                })
                vals = {'task_id': new_task_id}
                case_obj.write(cr, uid, [bug.id], vals)
                case_obj.case_open(cr, uid, [bug.id])

        return  {
            'name': _('Tasks'),
            'view_type': 'form',
            'view_mode': 'form,tree', 
            'res_model': 'project.task',
            'res_id': int(new_task_id),
            'view_id': False,
            'views': [(id2,'form'),(id3,'tree'),(False,'calendar'),(False,'graph')],
            'type': 'ir.actions.act_window',
            'search_view_id': res['res_id'],
            'nodestroy': True
        }

    def convert_issue_task_tree(self, cr, uid, ids, context=None):
        """Create Task from Issue, without opening it's form"""
        self.convert_issue_task(cr, uid, ids, context=context)
        return True

project_issue()


class crm_case_categ(osv.osv):
    _inherit = "crm.case.categ"

    #FUTURE: add behaviour to "Base"
    def name_get(self, cr, uid, ids, context=None):
        context = context or {}
        ids = ids or []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res
        
    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'note': fields.text('Description', size=64),
        'parent_id': fields.many2one('crm.case.categ', 'Parent'),
        'child_ids': fields.many2many('crm.case.categ', 'crm_case_categ_parent_rel', 'parent_id', 'categ_id', 'Child Categories'),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
        'code': fields.char('Code', size=10),
        'allow_issues': fields.boolean('Allow Issues', help="Selectable to categoriza issues"),
    }
    
crm_case_categ()
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


