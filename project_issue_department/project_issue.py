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

from osv import fields, osv

    
class project_issue(osv.osv):
    _inherit = 'project.issue'
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
    }
    
    def on_change_project(self, cr, uid, ids, proj_id=False, context=None):
        """When changing the Issue's Project:
            - the Department is copied from the Project
        """
        super_res = super(project_issue, self).on_change_project(cr, uid, ids, proj_id, context = context)
        data = super_res.get('value', {})
        if proj_id:
            proj_obj = self.pool.get('project.project').browse(cr, uid, proj_id, context)
            if proj_obj.department_id:
                data.update( {'department_id': proj_obj.department_id.id} )
        return {'value': data}

project_issue()

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


