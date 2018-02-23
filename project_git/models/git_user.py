# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields, api
from ..utils.utils import get_image_type


class GitUser(models.Model):
    _name = "project.git.user"

    name = fields.Char(
        string="Name",
        size=256
    )

    username = fields.Char(
        string="Username",
        size=256,
        index=True,
    )

    email = fields.Char(
        string="Email",
        size=128,
        index=True,
    )

    uuid = fields.Char(
        string="UUID",
        size=256
    )

    avatar = fields.Char(
        string="Avatar"
    )

    url = fields.Char(
        string="URL"
    )

    type = fields.Selection(
        selection=[],
        string="Type",
        index=True,
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Related User',
    )

    repository_ids = fields.One2many(
        comodel_name="project.git.repository",
        string="Repositories",
        inverse_name="user_id"
    )

    image_type = fields.Char(
        string="Type",
        compute="_compute_image_type"
    )

    @api.multi
    @api.depends("type")
    def _compute_image_type(self):
        get_image_type(self)
