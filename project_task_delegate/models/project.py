# -*- coding: utf-8 -*-
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _


class Task(models.Model):
    _inherit = 'project.task'

    delegated_user_id = fields.Many2one(
        'res.users', related='child_ids.user_id', string='Delegated To')

    @api.multi
    def _delegate_task_attachments(self, delegated_task_id):
        """
        Duplicates parent attachments to child.
        """
        self.ensure_one()
        attachment = self.env['ir.attachment']
        attachment_ids = attachment.search(
            [('res_model', '=', self._name), ('res_id', '=', self.id)])
        new_attachment_ids = []
        for attachment_id in attachment_ids:
            new_attachment_ids.append(attachment_id.copy(
                default={'res_id': delegated_task_id.id}))
        return new_attachment_ids

    @api.model
    def _prepare_delegate_values(self, delegate_data):
        delegate_values = {}
        delegate_values[self.id] = {
            'name': delegate_data['name'],
            'project_id': delegate_data['project_id'] and
            delegate_data['project_id'][0] or False,
            'stage_id': delegate_data.get('stage_id') and
            delegate_data.get('stage_id')[0] or False,
            'user_id': delegate_data['user_id'] and
            delegate_data['user_id'][0] or False,
            'planned_hours': delegate_data['planned_hours'] or 0.0,
            'parent_ids': [(6, 0, [self.id])],
            'description': delegate_data['new_task_description'] or '',
            'child_ids': [],
            'remaining_hours': delegate_data['planned_hours_me'],
            # The values below will be written on the old task.
            'task_planned_hours': delegate_data['planned_hours_me'],
            'task_name': delegate_data['prefix'] or ''
        }
        return delegate_values

    @api.model
    def do_delegate(self, delegate_data=None):
        """
        Delegate Task to another users.
        """
        if delegate_data is None:
            delegate_data = {}
        assert delegate_data['user_id'], _(
            "Delegated User should be specified")
        delegated_tasks = {}
        vals = self._prepare_delegate_values(delegate_data)
        for task in self:

            delegated_task_id = self.copy({
                'name': vals[task.id]['name'],
                'project_id': vals[task.id]['project_id'],
                'stage_id': vals[task.id]['stage_id'],
                'user_id': vals[task.id]['user_id'],
                'planned_hours': vals[task.id]['planned_hours'],
                'parent_ids': vals[task.id]['parent_ids'],
                'description': vals[task.id]['description'],
                'child_ids': vals[task.id]['child_ids'],
            })
            task._delegate_task_attachments(delegated_task_id)

            task.write({
                'remaining_hours': vals[task.id]['remaining_hours'],
                'planned_hours': vals[task.id]['task_planned_hours'],
                'name': vals[task.id]['task_name']
            })
            delegated_tasks[task.id] = delegated_task_id.id
        return delegated_tasks
