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
        Input parameters:
            ids:            database ids of the objects
            model_name:     target model, eg. 'project.issue' or 'crm.claim'
            override_flds:  fields to try getting a user_id, beforr trying profiling rules. This overrides the rules.
            default_flds:   fields to try getting a user_id, id none is found by rules or override_flds:
            user_fld:       field in the model storing the user. Defaults to 'user_id'.
            force:          force profiling rules, even if user_id is not empty
        
        Note: User admin(id=1) is ignored when checking.
        
        Returns a list of dictionaries with:
            'id':   the object id
            'vals': dictionay of values containing the user id, that can be passed to a write operation
            Example: [ {'id': 22, vals: { 'user_id': 2}} 
                     , {'id': 23, vals: { 'user_id': 2}} ]
        """
        obj_model = self.pool.get(model_name)
        if type(ids) == int : ids = [ids] #Ensure ids is a list
        res = []
        for item in obj_model.browse(cr, uid, ids, context=context):
            #0. Check forcing rule: step over if no forcea nd user_id already assigned
            if not force and item[user_fld]:
                break

            user = None
            #1. Evaluate fields overriding rules
            if not user:
                for f in override_flds:
                    try:
                        user = eval('item.' + f + '.id')
                        if user==1: user = None #Ignore admin user
                    finally:
                        if user: break
            #2. Evaluate profiling rules
            if not user:
                dept = item.department_id and item.department_id.id
                team = item.section_id and item.section_id.id
                rule = self.search(cr, uid, [('department_id', '=', dept), ('section_id', '=', team)], context=context)
                user = rule and self.browse(cr, uid, rule[0], context=context).user_id.id
            #3. Evaluate fields defaults
            if not user:
                for f in default_flds:
                    try:
                        user = eval('item.' + f + '.id')
                        if user==1: user = None #Ignore admin user
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
        
        Intended to be used from Server Actions.
        Warning: do not call from write() method - it will cause infinite recursion.
        """
        if not context: context = {}
        if context.get('__profiling_action'):
            return False #Prevent infinite recursion from the obj_model.write() call below
        context.update( { '__profiling_action':1 } )
        obj_model = self.pool.get(model_name)
        recs = self.get_user_id(cr, uid, ids, model_name, user_fld=user_fld, override_flds=override_flds, default_flds=default_flds, force=force, context=context)
        for item in recs:
            obj_model.write(cr, uid, [ item['id'] ], item['vals'], context=context)
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


class project_issue(osv.osv):
    _inherit = 'project.issue'

    def create(self, cr, uid, vals, context={}):
        rec_id = super(project_issue, self).create(cr, uid, vals, context)
        #Profiling applied after record is created
        self.pool.get('project.issue.profiling').set_user_id(
            cr, uid, [rec_id], 'project.issue', 
            override_flds = ['project_id.user_id'], #Project manager overrides rules
            default_flds  = ['section_id.user_id'], #Assign to Team Manager if no rule found
            context=context)
        return rec_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(project_issue, self).write(cr, uid, ids, vals, context)
        #Profiling applied after record is updated
        self.pool.get('project.issue.profiling').set_user_id(
            cr, uid, ids, 'project.issue', 
            override_flds = ['project_id.user_id'], #Project manager overrides rules
            default_flds  = ['section_id.user_id'], #Assign to Team Manager if no rule found
            context=context)
        return res

project_issue()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
