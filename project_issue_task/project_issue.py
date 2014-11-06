# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2013 Daniel Reis
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

from openerp.osv import orm
from openerp import _


class project_issue(orm.Model):
    _inherit = 'project.issue'

    def action_create_task(self, cr, uid, ids, context=None):
        """
        Create and a related Task for the visit report, and open it's Form.
        """
        rec = self.browse(cr, uid, ids[0], context)
        assert not rec.task_id, _("A Task is already assigned to the Issue!")

        rec_fields = ['project_id', 'analytic_account_id', 'location_id']
        task_data = dict([(x, getattr(rec, x).id) for x in rec_fields
                          if hasattr(rec, x) and getattr(rec, x)])
        task_data['name'] = _('Report for %s') % rec.name
        task_data['issue_id'] = rec.id
        task_data['categ_ids'] = [(6, 0, [x.id for x in rec.categ_ids])]

        task_model = self.pool.get('project.task')
        task_id = task_model.create(cr, uid, task_data, context=context)
        rec.write({'task_id': task_id}, context=context)
        res = {
            'name': _('Issue Task Report'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task',
            'res_id': task_id,
            'type': 'ir.actions.act_window'}
        return res

    def case_cancel(self, cr, uid, ids, context=None):
        """ On Issue Cancel, also Cancel Task """
        task_ids = [issue.task_id.id
                    for issue in self.browse(cr, uid, ids, context=context)
                    if issue.task_id]
        self.pool.get('project.task').case_cancel(
            cr, uid, task_ids, context=context)
        return super(project_issue, self).case_cancel(
            cr, uid, ids, context=context)
