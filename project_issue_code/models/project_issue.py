# -*- coding: utf-8 -*-
# © 2016 Michael Viriyananda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm


class project_issue(orm.Model):
    _inherit = 'project.issue'

    _columns = {
        'issue_code': fields.char(
            'Issue Code', required=True, readonly=True,
        ),
        'accepted_date': fields.datetime(
            'Accepted date', readonly=True, select=True,
        ),
    }

    _defaults = {
        'issue_code': "/",
    }

    def write(self, cr, uid, ids, vals, context=None):
        project_task_type_ob = self.pool.get('project.task.type')
        if type(ids) is list:
            issue_id = ids[0]
        else:
            issue_id = ids
        issue = self.browse(cr, uid, issue_id, context=context)
        if issue.issue_code == '/' and 'stage_id' in vals:
            task_type = project_task_type_ob.browse(
                cr, uid, vals['stage_id'], context=context
            )
            if task_type.set_issue_code:
                vals['issue_code'] = self.pool.get('ir.sequence').get(
                    cr, uid, 'project.issue'
                )
                vals['accepted_date'] = fields.datetime.now()
        return super(project_issue, self).write(cr, uid, ids, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['issue_code'] = '/'
        return super(project_issue, self).copy(cr, uid, id, default)
