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

from crm import crm
from osv import fields, osv
from datetime import datetime, timedelta
import reis_base as util

TASK_TYPE_USE_GROUPS = [('resolution', 'Resolution Stage'), ('cause', 'Problem Cause')]
class project_task_type(osv.osv):
    _inherit = 'project.task.type'
    _sort = 'use_group, sequence'
    _columns = {
        'use_group': fields.selection( TASK_TYPE_USE_GROUPS , 'Usage', size=16),
        'code': fields.char('Code', size=10),
    }
project_task_type()


class project_functional_block(osv.osv):
    _inherit = 'project.functional_block'
    _columns = {
        'code': fields.char('Code', size=10),
    }
project_functional_block()


#----------------------------------------------------------
# Project
#   * Field to assign Code (.ref)
#----------------------------------------------------------
class project(osv.osv):
    _inherit = 'project.project'
    _columns = {
        'project_code': fields.char('Project Code(s)', size=128, help='Project management specific identification codes.'),
        'department_id': fields.many2one('hr.department', 'Department', help="Organization unit owner of the project"),
        #Disabled, for now:'product_id': fields.many2one('product.product', 'Reference Product'),
        #Disabled, for now: 'location_id': fields.many2one('stock.location', 'Location', help="Project's main location for delivery or product installation"),
    }

    def name_get(self, cr, uid, ids, context=None):
        return util.ext_name_get(self, cr, uid, ids, '[%(project_code)s] %(name)s', ['project_code', 'name'], context=context)
        
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        return util.ext_name_search(self, cr, user, name, args, operator, context=context, limit=limit, 
                                keys=['project_code', 'name', 'code'])
    
project()


#----------------------------------------------------------
# Project task
#   * can be mapped to an issue
#----------------------------------------------------------
class task(osv.osv):
    #FUTURE: use task recurrency, to generate maintenance plans
    #FUTURE: Apply maintenance plan templates (use Project templates?)
    _inherit = "project.task"
    _columns = {
        #standard fields (changing texts or domains):
        'section_id': fields.many2one('crm.case.section', 'Service Team', select=True,\
            help='Service team to which Task belongs to.'), #standard: relabeled
        'functional_block_id': fields.many2one('project.functional_block', 'Component', help = "Component (system, module, function) to be adressed"),
        'priority': fields.selection(crm.AVAILABLE_PRIORITIES, 'Priority', select=True), #Standard is 0-4; changed to conform with project_issue (1-5)!
        #added fields:
        'ref': fields.char('Code', 20, help="Service Order number"),
        'issue_id': fields.many2one('project.issue', 'Related Issue', 
            help="Issue related to this task"),
        'report_desc': fields.text('Task report description'),
        'todo_desc': fields.text('Pending issues description'),
        'categ_id': fields.many2one('crm.case.categ', 'Category'), ### domain="[('object_id.model', '=', 'crm.project.bug')]"),
        'type_id': fields.many2one('project.task.type', 'Resolution Stage', domain="[('use_group', '=', 'resolution')]"),
        'reason_id': fields.many2one('project.task.type', 'Problem Cause', domain="[('use_group', '=', 'cause')]", \
            help='Cause for the incident that made this task necessary. Avaliable list depends on the Task Type.'),
        'department_id': fields.related('project_id', 'department_id', string = 'Department', type="many2one", relation="hr.department", store=True, select=True),
        'material_ids': fields.one2many('project.task.materials', 'task_id', 'Materials used'),
    }

    def _set_issue_state(self, cr, uid, ids, state, context = None):
        """
        Update the state of the related Issues.
        Will not affect Issues already Closed or Cancelled.
        Ignores Tasks with no related issue.

        ids:    list of task_ids
        state:  state to apply to the related issues
        return: list with issues_ids of the changed Issues
        """
        #Exit if no Ids
        if not ids:
            return False
            
        #List selected task objects
        tasks = [x for x in self.browse(cr, uid, ids)]

        #List and update Issue's states
        issue_obj = self.pool.get('project.issue')
        issues = [task.issue_id.id
                  for task in tasks 
                  if task.issue_id and task.issue_id.state not in ('closed', 'cancelled')
                 ]
        if issues:
            if state == 'pending': issue_obj.case_pending(cr, uid, issues)
            if state == 'open': issue_obj.case_open(cr, uid, issues)
            if state == 'close': issue_obj.case_close(cr, uid, issues)

        #List and create Issues for each Task with pending actions
        #TODO
        for task in tasks:
            if not task.issue_id and task.todo_desc:
                issue_id = issue_obj.create(cr, uid, {
                    'categ_id': task.categ_id.id,
                    'date_deadline': task.date_deadline,
                    'description': task.todo_desc,
                    'name': task.name,
                    'project_id': task.project_id.id,
                    'partner_id': task.project_id.partner_id.id,
                    'section_id': task.section_id.id,
                    'user_id': task.user_id.id,
                },context=context)
                ###rint 'Created new Issue:', task.id, task.todo_desc, issue_id
                self.write(cr, uid, [task.id], {'issue_id': issue_id}, context)

        return True

    def do_pending(self, cr, uid, ids, context=None):
        self._set_issue_state(cr, uid, ids, 'pending')
        return super(task, self).do_pending(cr, uid, ids)

    #do_delegate: 
    #   no changes
        
    def do_close(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        #Ensure that "ids" is a list
        if type(ids) != type([]):
            ids = [ids]
        #Pending Issues: if Task is closed with ToDos
        tasks_pending_issue = [t.id 
                              for t in self.browse(cr, uid, ids) 
                              if t.type_id and t.type_id.code and t.type_id.code[:2]!='OK']
        self._set_issue_state(cr, uid, tasks_pending_issue, 'pending')
        #Closed Issues; all the others
        tasks_close_issue = list( set(ids) - set(tasks_pending_issue) )
        self._set_issue_state(cr, uid, tasks_close_issue, 'close')
        #End
        
        #Automatically adjust Task Start and End dates based on Work details
        for t in  self.browse(cr, uid, ids, context=context):
            task_dts, task_dte = t.date_start, t.date_end
            for w in t.work_ids:
                #Task start date should not be later than the oldest work line
                work_dts = w.date
                task_dts = min(task_dts, work_dts) or work_dts
                #Task end date shold not be before the last work line
                d = datetime.strptime(w.date, '%Y-%m-%d %H:%M:%S') \
                    + timedelta(seconds=round(w.hours*3600) )
                work_dte = d.strftime('%Y-%m-%d %H:%M:%S')
                task_dte = max(task_dte, work_dte) or work_dte
            vals = {}
            if task_dts: vals.update({ 'date_start': task_dts})
            if task_dte: vals.update({ 'date_end': task_dte})
            if vals: self.write(cr, uid, [t.id],vals, context=context)
        
        return super(task, self).do_close(cr, uid, ids, context)
        
    def do_reopen(self, cr, uid, ids, context=None):
        self._set_issue_state(cr, uid, ids, 'open')
        return super(task, self).do_reopen(cr, uid, ids, context)

    def do_cancel(self, cr, uid, ids, *args):
        self._set_issue_state(cr, uid, ids, 'pending')
        return super(task, self).do_cancel(cr, uid, ids, *args)

    def do_open(self, cr, uid, ids, *args):
        self._set_issue_state(cr, uid, ids, 'open')
        return super(task, self).do_open(cr, uid, ids, *args)

    def do_draft(self, cr, uid, ids, *args):
        self._set_issue_state(cr, uid, ids, 'pending')
        return super(task, self).do_draft(cr, uid, ids, *args)

    def action_auto_assign(self, cr, uid, ids):
        """Assign Task and Notify the user.
        
        Task must have Project and Issue.
        The Project must have a Department.
        The Issue must have a Section.
        Ellegible users must have Section and Department.
        
        List all Tasks in Draft state, having:with Section tasks?
        - Department: task.project_id.department_id.id
        - Section: task.issue_id.section_id.id

        For each Task:
            List the ellegigle users, matching section_id and (optional) department_id.
            Skip if current Task assignee is in the list.
            Add first user on the List to an Action List
            
        For each item on the Action List:
            Assign task to the user.
            E-mail the user informing the assignment.
        
        """
        return True
    
task()


class project_work(osv.osv):
    _inherit = "project.task.work"

    #Deprecated: now using Start Dtateime + Duratuin instead, to avoid issues with UTC Time 
    #_columns = {
    #    'time_from': fields.float('Time From'),
    #    'time_to': fields.float('Time To'),
    #}
    _defaults = {
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d'), #Changed default
    }
project_work()


class project_task_materials(osv.osv):
    _name = "project.task.materials"
    _description = "Project Task Materials Used"
    _inherits = {'account.analytic.line': 'line_id'}

    _columns = {
        'task_id': fields.many2one('project.task', 'Task', ondelete='cascade', required=True),
        'line_id': fields.many2one('account.analytic.line', 'Analytic line', ondelete='cascade', required=True),
    }
    _defaults = {
        'journal_id': lambda self, cr, uid, ctx: 
            self.pool.get('ir.model.data').get_object(cr, uid, 'hr_timesheet', 'analytic_journal').id,
    }
    def create(self, cr, uid, vals, *args, **kwargs):
        task_model = self.pool.get('project.task')
        task_doc = task_model.browse( cr, uid, [vals['task_id']] )[0]
        prod_model = self.pool.get('product.product')
        prod_doc = prod_model.browse( cr, uid, [vals['product_id']] )[0]

        vals.update( 
            { 'name': task_doc.name
            , 'account_id': task_doc.project_id.analytic_account_id.id
            , 'product_uom_id': prod_doc.uom_id.id
            , 'general_account_id': prod_doc.product_tmpl_id.property_account_expense.id
                                 or prod_doc.categ_id.property_account_expense_categ.id
            , 'to_invoice': task_doc.project_id.analytic_account_id.to_invoice
                        and task_doc.project_id.analytic_account_id.to_invoice.id
            } )
        return super(project_task_materials, self).create(cr, uid, vals, *args, **kwargs)

project_task_materials()


class res_partner(osv.osv):
    _inherit = 'res.partner'

    def name_get(self, cr, uid, ids, context=None):
        return util.ext_name_get(self, cr, uid, ids, '[%(ref)s] %(name)s', ['ref', 'name'], context=context)
        
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        return util.ext_name_search(self, cr, user, name, args, operator, context=context, limit=limit, 
                                keys=['ref','name'])

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


