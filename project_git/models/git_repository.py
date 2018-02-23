# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import string
import random
import uuid

from odoo import models, fields, api
from ..utils.utils import get_image_type, get_avatar, urljoin


class GitRepository(models.Model):
    _name = 'project.git.repository'

    def _default_secret(self):
        alphabet = string.ascii_letters + string.digits
        secret = ''.join(
            random.SystemRandom().choice(alphabet) for i in range(30)
        )
        return secret

    name = fields.Char(
        string='Name',
        size=256,
    )

    repo_name = fields.Char(related="name")

    uuid = fields.Char(
        string='UUID',
        size=256,
        index=True,
    )

    full_name = fields.Char(
        string='Full Name',
        size=256
    )

    odoo_uuid = fields.Char(
        string='UUID',
        size=256,
        default=lambda *a: uuid.uuid4(),
        index=True,
    )

    avatar = fields.Char(
        string='Avatar',
        compute='_compute_avatar',
    )

    url = fields.Char(
        string='URL',
        default='#'
    )

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        required=True,
        index=True,
    )

    branch_ids = fields.One2many(
        comodel_name='project.git.branch',
        string='Branches',
        inverse_name='repository_id'
    )

    branch_count = fields.Integer(
        compute="_compute_branch_count"
    )

    user_id = fields.Many2one(
        comodel_name='project.git.user',
        string='Owner',
        ondelete='cascade',
        index=True,
    )

    type = fields.Selection(
        selection=[],
        string='Type',
        index=True,
    )

    webhook_url = fields.Char(
        string='Webhook Url',
        compute='_compute_webhook_url',
    )

    secret = fields.Char(
        default=lambda s: s._default_secret()
    )

    use_secret = fields.Boolean(
        compute='_compute_use_secret'
    )

    image_type = fields.Char(
        string='Type',
        compute='_compute_image_type'
    )

    @api.multi
    @api.depends("branch_ids")
    def _compute_branch_count(self):
        for rec in self:
            rec.branch_count = len(rec.branch_ids)

    @api.multi
    @api.depends('type')
    def _compute_avatar(self):
        get_avatar(self, 'repository')

    @api.multi
    @api.depends('type')
    def _compute_use_secret(self):
        secret_types = self._secret_visible_for_types()
        for rec in self:
            rec.use_secret = rec.type in secret_types

    def _secret_visible_for_types(self):
        return []

    @api.multi
    @api.depends('type')
    def _compute_image_type(self):
        get_image_type(self)

    @api.onchange('project_id', 'type')
    def _onchange_name_components(self):
        if not self.project_id or self.type:
            return
        self.name = '%s - %s' % (
            self.project_id.key, self._get_selection_label(self.type)
        )

    def _get_selection_label(self, type):
        for item in self._fields['type'].selection:
            if item[0] == type:
                return item[1]
        return ''

    @api.multi
    @api.depends('odoo_uuid', 'type')
    def _compute_webhook_url(self):
        base_url = self.env['ir.config_parameter']\
            .sudo()\
            .get_param('web.base.url')
        for record in self:
            if record.type:
                record.webhook_url = urljoin(
                    base_url, record.type, 'payload', record.odoo_uuid
                )
