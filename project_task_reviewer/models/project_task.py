# -*- coding: utf-8 -*-
# © 2018 RGB Consulting - <odoo@rgbconsulting.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Task(models.Model):
    _inherit = 'project.task'

    reviewer_id = fields.Many2one(comodel_name='res.users', string='Reviewer',
                                  default=lambda self: self.env.uid,
                                  index=True, track_visibility='always')

    @api.model
    def _message_get_auto_subscribe_fields(self, updated_fields,
                                           auto_follow_fields=None):
        if auto_follow_fields is None:
            auto_follow_fields = ['user_id', 'reviewer_id']
        return super(Task, self)._message_get_auto_subscribe_fields \
            (updated_fields, auto_follow_fields)
