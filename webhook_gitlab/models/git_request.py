# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class GitRequest(models.Model):
    _name = 'git.request'

    task_id = fields.Many2one('project.task', ondelete='cascade')
    ticket_id = fields.Many2one('helpdesk.ticket', ondelete='cascade')
    id_request = fields.Integer(
        string='Request ID',
        help='Technical field used to track the merge request id')
    id_project = fields.Integer(
        string='Project ID',
        help='Technical field used to track the project id in Gitlab')
    name = fields.Char(string='Title')
    wip = fields.Boolean(string='WIP')
    branch = fields.Char()
    last_commit = fields.Char()
    approved = fields.Boolean()
    state = fields.Selection([
        ('opened', 'Opened'),
        ('merged', 'Merged'),
        ('closed', 'Closed'),
        ('locked', 'Locked'),
    ])
    ci_status = fields.Selection([
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
        ('canceled', 'Canceled'),
        ('unknown', 'Unknown'),
    ], default='pending', string="CI Status")
    url = fields.Char()
    user_id = fields.Many2one('res.users', string="Created by")

    @api.multi
    def open_merge_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.url,
        }
