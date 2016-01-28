# -*- coding: utf-8 -*-
# © 2014 Daniel Reis (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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
