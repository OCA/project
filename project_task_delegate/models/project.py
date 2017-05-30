# -*- coding: utf-8 -*-
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _


class Task(models.Model):
    _inherit = 'project.task'

    delegated_user_id = fields.Many2one(
        'res.users', related='child_ids.user_id', string='Delegated To')

    @api.multi
    def _delegate_task_attachments(self, delegated_task):
        """
        Duplicates parent attachments to child.
        """
        self.ensure_one()
        attachment = self.env['ir.attachment']
        attachment_ids = attachment.search(
            [('res_model', '=', self._name), ('res_id', '=', self.id)])
        new_attachments = []
        for attachment_id in attachment_ids:
            new_attachments.append(attachment_id.copy(
                default={'res_id': delegated_task.id}))
        return new_attachments

    @api.model
    def _prepare_delegate_values(self, delegate_data):
        """
        Prepare the child task values.
        """
        return {
            'name': delegate_data['name'],
            'project_id': delegate_data['project_id'] and
            delegate_data['project_id'][0] or False,
            'stage_id': delegate_data.get('stage_id') and
            delegate_data.get('stage_id')[0] or False,
            'user_id': delegate_data['user_id'] and
            delegate_data['user_id'][0] or False,
            'parent_ids': [(6, 0, [self.id])],
            'description': delegate_data['new_task_description'] or '',
            'child_ids': [],
        }

    @api.model
    def do_delegate(self, delegate_data=None):
        """
        Delegate Task to another users.
        """
        if delegate_data is None:
            delegate_data = {}
        assert delegate_data['user_id'], _(
            "Delegated User should be specified")
        vals = self._prepare_delegate_values(delegate_data)
        delegated_task = self.copy(vals)
        self._delegate_task_attachments(delegated_task)
        self.write({
            'remaining_hours': delegate_data['planned_hours_me'] or 0.0,
            'planned_hours': delegate_data['planned_hours_me'] +
            (self.effective_hours or 0.0),
            'name': delegate_data['prefix'] or '',
        })
        return delegated_task.id
