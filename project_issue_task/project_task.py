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

from openerp.osv import fields, orm


class task(orm.Model):
    _inherit = "project.task"

    def _fld_issue_id(self, cr, uid, ids, field, arg, context=None):
        res = {}
        issue_model = self.pool.get('project.issue')
        for doc in self.browse(cr, uid, ids, context=context):
            issue_id = issue_model.search(
                cr, uid, [('task_id', '=', doc.id)], context=context)
            if issue_id:
                res[doc.id] = issue_id[0]
            else:
                res[doc.id] = None
        return res

    _columns = {
        'issue_id': fields.function(
            _fld_issue_id, string="Related Issue",
            type="many2one", relation="project.issue", store=True),
        'ref': fields.char('Reference', 20),
        'reason_id': fields.many2one('project.task.cause', 'Problem Cause'),
        }

    def action_close(self, cr, uid, ids, context=None):
        """ On Task Close, also close Issue """
        issue_ids = [x.issue_id.id
                     for x in self.browse(cr, uid, ids, context=context)
                     if x.issue_id]
        self.pool.get('project.issue').case_close(
            cr, uid, issue_ids, context=context)
        return super(task, self).action_close(cr, uid, ids, context=context)
