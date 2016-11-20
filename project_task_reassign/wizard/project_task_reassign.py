# -*- coding: utf-8 -*-
# Copyright 2013 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import fields, osv
from openerp.tools.translate import _


class project_task_reassign(osv.TransientModel):
    _name = 'project.task.reassign'
    _description = 'Task Reassign'

    _columns = {
        'project_id': fields.many2one(
            'project.project', 'Project',
            help="Project this task should belong to"),
        'user_id': fields.many2one(
            'res.users', 'Assign To',
            help="User you want to assign this task to"),
        }

    def reassign(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        task_ids = context.get('active_ids') or [context.get('active_id')]
        assert task_ids, _("No active Tasks found.")
        assign_to = self.browse(cr, uid, ids, context=context)[0]
        return self.pool.get('project.task').do_reassign(
            cr, uid, task_ids,
            assign_to.user_id and assign_to.user_id.id or None,
            assign_to.project_id and assign_to.project_id.id or None,
            context=context)
