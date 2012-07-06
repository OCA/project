# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis, 2012
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
from openerp import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


class project_issue_profiling(osv.osv):
    _name = "project.issue.profiling"
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department',\
            help="Organization unit of the issue's subject"),
        'section_id': fields.many2one('crm.case.section', 'Service Team', select=True, \
            help='Team to handle the case.'),
        'user_id': fields.many2one('res.users', 'User', \
            help="User to assign as responsible for the issues"),
        'notes': fields.text('Notes'),
    }

    def get_user_id(self, cr, uid, ids, model_name, override_flds=[], default_flds=[], user_fld='user_id', force=False, context={}):
        """Get user_ids responsible for a list of documents
        If there is already an assigned user, it does nothing. Use 'force' if you want to override this.
        Superuser (admin) is ignored (considered equivalent to None) when checking override_flds and default_flds.
        
        Input parameters:
            ids:            database ids of the objects
            model_name:     target model, eg. 'project.issue' or 'crm.claim'
            override_flds:  fields to try getting a user_id, before trying profiling rules. This overrides the rules.
            default_flds:   fields to try getting a user_id, id none is found by rules or override_flds.:
                            Default to the Team manager (section_id.user_id), if available.
            user_fld:       field in the model to store the assigned user. Defaults to 'user_id'.
            force:          force profiling rules, even if user_id is not empty
        
        Returns a list of dictionaries with:
            'id':   the object id
            'vals': dictionay of values containing the user id, that can be passed to a write operation
        Example: 
            [ { 'id': 22,
                ''vals'': { 'user_id': 2} 
              }, 
              {'id': 23, 
               ''vals'': { 'user_id': 2}
              } ]
        """
        #Ensure ids is a list        
        if type(ids) == int : 
            ids = [ids] 
        #Ensure model_name is provided and browse object
        if not model_name: 
            raise('ERROR: Model name must be provided.')
        else:
            obj_model = self.pool.get(model_name)
        #default_flds defaults to section_id.user_id
        if not default_flds:
            default_flds = ['section_id.user_id']
        #For each record, calculate the user_id to assign
        res = []
        for item in obj_model.browse(cr, uid, ids, context=context):
            user = None
            #0. Stop if user_id already assigned; unless 'force' is specified
            if not force and item[user_fld]:
                break
            #1. Check override field
            if not user:
                for f in override_flds:
                    try:
                        user = eval('item.' + f + '.id')
                        if user == SUPERUSER_ID: user = None #Ignore admin user
                    finally:
                        if user: break
            #2. Check profiling rules
            if not user:
                dept = item.department_id and item.department_id.id
                team = item.section_id and item.section_id.id
                rule = self.search(cr, uid, [('department_id', '=', dept), ('section_id', '=', team)], context=context)
                user = rule and self.browse(cr, uid, rule[0], context=context).user_id.id
            #3. Check fields for defaults, if no user found until now
            if not user:
                for f in default_flds:
                    try:
                        user = eval('item.' + f + '.id')
                        if user == SUPERUSER_ID: user = None #Ignore admin user
                    finally:
                        if user: break
            #4. Update result list
            if user:
                res.append( {'id': item.id, 'vals': { user_fld: user} } )
        return res
        
    def set_user_id(self, cr, uid, ids, model_name, override_flds=[], default_flds=[], user_fld='user_id', force=False, context=None):
        """Gets and writes user_ids responsible for a list of documents
        Inputs:  see "get_user_id"
        Returns: True if executed
        Intended to be used from Server Actions. Example:
                Object:         project.issue.profiling
                Action Type:    Python Code
                Python Code:    self.set_user_id(cr, uid, [context.get('active_id')], 'project.issue', override_flds=['project_id.user_id'], context=context)
        """
        if not context: 
            context = {}
        #Prevent infinite recursion from the obj_model.write()
        if context.get('__profiling_action'):
            return False 
        context.update( { '__profiling_action':1 } )
        obj_model = self.pool.get(model_name)
        recs = self.get_user_id(cr, uid, ids, model_name, user_fld=user_fld, override_flds=override_flds, default_flds=default_flds, force=force, context=context)
        for item in recs:
            obj_model.write(cr, uid, [ item['id'] ], item['vals'], context=context)
            _logger.debug('Profiling responsible assigned on model %s, id %d' % (model_name, item['id']) )
        return True

project_issue_profiling()


class hr_department(osv.osv):
    _inherit = 'hr.department'
    _columns = {
        'issue_profiling': fields.one2many('project.issue.profiling', 'department_id', 'Issue Profiling Rules'),
    }
hr_department()


class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'issue_profiling': fields.one2many('project.issue.profiling', 'user_id', 'Issue Profiling Rules'),
    }
res_users()


#class project_issue(osv.osv):
#    _inherit = 'project.issue'
#    
#    def action_profile(self, cr, uid, ids, context={}):
#        #Profiling applied after record is created
#        #Use in a Server Action with code: self.action_profile(cr, uid, [context.get('active_id')], context=context)
#        profiler_obj = self.pool.get('project.issue.profiling')
#        res = profiler_obj.set_user_id(
#            cr, uid, ids, 'project.issue', 
#            override_flds = ['project_id.user_id'], #Project manager overrides rules
#            #default_flds  = ['section_id.user_id'], #Assign to Team Manager if no rule found
#            context=context)
#        return res
#
#project_issue()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
