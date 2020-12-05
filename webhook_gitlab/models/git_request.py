# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class GitRequest(models.Model):
    _name = 'git.request'
    _description = 'Information for Pull/Merge Requests'

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

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        rec.assing_tags()
        return rec

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        self.assing_tags()
        return res

    @api.multi
    def assing_tags(self):
        for rec in self:
            tags = []
            record = rec.task_id or rec.ticket_id
            tag_model = record.tag_ids._name
            current_tags = self.env[tag_model]
            current_tags |= record.tag_ids.filtered(
                lambda t: t.name.startswith('MR:') or t.name.startswith('CI:'))
            for tag in current_tags:
                tags.append((3, tag.id, 0))
            # Create prefix to have a base to get the external ID.
            # Possible values of prefix:
            # 'webhook_gitlab.project_tags_' or 'webhook_gitlab.helpdesk_tag_'
            prefix = 'webhook_gitlab.' + tag_model.replace('.', '_') + '_'
            # Get CI status tag.
            tags.append((4, self.env.ref(prefix + rec.ci_status).id, 0))
            # Get MR state tag.
            tags.append((4, self.env.ref(prefix + rec.state).id, 0))
            if rec.approved:
                tags.append((4, self.env.ref(prefix + 'approved').id, 0))
            else:
                tags.append((3, self.env.ref(prefix + 'approved').id, 0))
            if rec.wip:
                tags.append((4, self.env.ref(prefix + 'wip').id, 0))
            else:
                tags.append((3, self.env.ref(prefix + 'wip').id, 0))
            record.write({
                'tag_ids': tags,
            })
