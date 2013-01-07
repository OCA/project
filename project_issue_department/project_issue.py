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

from osv import fields, orm


class project_issue(orm.Model):
    _inherit = 'project.issue'
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
    }

    def on_change_project(self, cr, uid, ids, proj_id=False, context=None):
        """When Project is changed: copy it's Department to the issue."""
        res = super(project_issue, self)\
            .on_change_project(cr, uid, ids, proj_id, context=context)
        dept = proj_id and \
            self.pool.get('project.project')\
            .browse(cr, uid, proj_id, context)\
            .getattr('department_id')
        if dept:
            res.setdefault('value', {})\
                .update({'department_id': dept.id})
        return res

project_issue()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


