# -*- coding: utf-8 -*-
# Copyright 2004-2010 Tiny SPRL <http://tiny.be>.
# Copyright 2017 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models
from odoo.tools.translate import _


class ProjectTimeboxEmpty(models.TransientModel):
    _name = 'project.timebox.empty'
    _description = 'Project Timebox Empty'

    name = fields.Char('Name', size=32)

    @api.model
    def _empty(self):
        close = []
        up = []
        timebox_model = self.env['project.gtd.timebox']
        task_model = self.env['project.task']

        if not self.env.context.get('active_id'):
            return {}

        timeboxes = timebox_model.search([])
        if not timeboxes:
            raise exceptions.UserError(
                _('No timebox child of this one!'))
        tasks = task_model.search([
            ('timebox_id', '=', self.env.context['active_id'])])
        for task in tasks:
            if (task.stage_id and task.stage_id.fold) \
                    or (task.user_id.id != self.env.uid):
                close.append(task.id)
            else:
                up.append(task.id)
        if up:
            task_model.browse(up).write({'timebox_id': timeboxes[0].id})
        if close:
            task_model.browse(close).write({'timebox_id': False})
        return {}
