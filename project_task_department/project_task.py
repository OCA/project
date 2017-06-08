# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Daniel Reis
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

from openerp import models, fields


class Task(models.Model):
    _inherit = 'project.task'
    department_id = fields.Many2one('hr.department', 'Department')

    # Using old-style api for onchange
    def onchange_project(self, cr, uid, ids, proj_id=False, context=None):
        """ When Project is changed: copy it's Department to the issue. """
        res = super(Task, self).onchange_project(
            cr, uid, ids, proj_id, context=context)
        res.setdefault('value', {})

        if proj_id:
            proj = self.pool.get('project.project').browse(
                cr, uid, proj_id, context)
            dept = getattr(proj, 'department_id', None)
            if dept:
                res['value'].update({'department_id': dept.id})
            else:
                res['value'].update({'department_id': None})

        return res
