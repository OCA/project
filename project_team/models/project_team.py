# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTeam(models.Model):
    _name = 'project.team'
    _description = 'Project Team'

    active = fields.Boolean(default=True)

    name = fields.Char(required=True)

    image = fields.Binary(attachment=True)

    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id
    )

    project_id = fields.Many2one(
        string='Project',
        comodel_name='project.project',
        help='Select a project if this team is project specific.'
    )

    user_ids = fields.Many2many(
        string='Members',
        comodel_name='res.users',
        column1='team_id',
        column2='user_id',
        relation='team_user_rel'
    )
