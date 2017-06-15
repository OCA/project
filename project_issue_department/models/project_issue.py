# -*- coding: utf-8 -*-
from openerp import fields, models


class ProjectIssue(models.Model):
    _inherit = 'project.issue'
    _columns = {
        'department_id': fields.Many2one('hr.department', 'Department'),
    }

    def on_change_project(self, cr, uid, ids, proj_id=False, context=None):
        """When Project is changed: copy it's Department to the issue."""
        res = super(ProjectIssue, self).on_change_project(
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
