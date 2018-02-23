# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields, api, _
from ..utils.utils import get_image_type, get_avatar


class GitCommit(models.Model):
    _name = "project.git.commit"

    name = fields.Char(
        string="Name",
        size=256,
        required=True,
        index=True,
    )

    author_id = fields.Many2one(
        comodel_name="project.git.user",
        string="Author",
        required=True,
        ondelete="cascade",
        index=True,
    )

    message = fields.Text(
        string="Message",
        required=True,
    )

    message_short = fields.Text(
        compute="_compute_message_short"
    )

    url = fields.Char(
        string="URL",
        required=True
    )

    date = fields.Datetime(
        string="Date",
        required=True
    )

    branch_id = fields.Many2one(
        comodel_name="project.git.branch",
        string="Branch",
        ondelete="cascade",
        index=True,
    )

    repository_id = fields.Many2one(
        comodel_name="project.git.repository",
        related="branch_id.repository_id",
        string="Repository",
        readonly=True,
        store=True,
    )

    task_ids = fields.Many2many(
        comodel_name="project.task",
        id1="commit_id",
        id2="task_id",
        relation="task_commit_rel",
        string="Tasks"
    )

    task_count = fields.Integer(
        compute="_compute_task_count"
    )

    author_username = fields.Char(
        string="Username",
        related="author_id.username"
    )

    author_avatar = fields.Char(
        string="Avatar",
        related="author_id.avatar"
    )

    type = fields.Selection(
        selection=[],
        string="Type",
        required=False,
        related="branch_id.type",
        store=True,
        index=True,
    )

    image_type = fields.Char(
        string="Type",
        compute="_compute_image_type"
    )

    avatar = fields.Char(
        string="Avatar",
        compute="_compute_avatar",
    )

    @api.multi
    def _compute_message_short(self):
        for rec in self:
            rec.message_short = rec.message and rec.message[:75] + " ..." or ""

    @api.multi
    @api.depends("task_ids")
    def _compute_task_count(self):
        for rec in self:
            rec.task_count = len(rec.task_ids)

    @api.multi
    @api.depends("type")
    def _compute_image_type(self):
        get_image_type(self)

    @api.multi
    def calculate_number(self):
        from random import randint
        return randint(0, 10)

    @api.multi
    def _compute_avatar(self):
        get_avatar(self, 'commit')

    def is_orphan(self):
        return len(self.task_ids) == 0

    @api.multi
    def open_tasks(self):
        self.ensure_one()

        action = self.env['ir.actions.act_window'].for_xml_id(
            'project', 'act_project_project_2_project_task_all'
        )

        action['display_name'] = action['name'] = _("Commit tasks")
        action['context'] = {
            'group_by': 'stage_id',
            'default_project_id': self.repository_id.project_id.id,
            'create': False,
        }
        action['domain'] = [('commit_ids', 'in', [self.id])]
        return action
