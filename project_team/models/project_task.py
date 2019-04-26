# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    project_team_id = fields.Many2one(
        string='Assigned Team',
        comodel_name='project.team'
    )

    project_team_user_ids = fields.Many2many(
        related='project_team_id.user_ids'
    )

    project_team_image = fields.Binary(
        related='project_team_id.image'
    )

    def default_user_ids(self):
        return [(4, self.env.user.id, 0)]

    user_ids = fields.Many2many(
        string='Assigned to',
        comodel_name='res.users',
        column1='task_id',
        column2='user_id',
        relation='task_user_rel',
        default=default_user_ids
    )

    @api.onchange('project_team_id')
    def onchange_project_team_id(self):
        if self.project_team_id:
            self.user_id = False
            self.user_ids = self.project_team_id.user_ids
