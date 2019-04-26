# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from json import dumps


class ProjectProject(models.Model):
    _inherit = 'project.project'

    user_ids = fields.Many2many(
        comodel_name='res.users',
        compute='_compute_user_ids'
    )

    user_ids_images = fields.Text(
        compute='_compute_user_ids'
    )

    project_team_id = fields.Many2one(
        string='Team',
        comodel_name='project.team'
    )

    @api.depends('project_team_id',
                 'task_ids',
                 'task_ids.project_team_user_ids',
                 'task_ids.user_id')
    def _compute_user_ids(self):
        for project in self:
            if project.project_team_id:
                project.user_ids = project.project_team_id.user_ids
                project.user_ids_images = dumps([(x.id, x.name) for x in project.user_ids])
            else:
                user_ids = self.env['res.users']
                for task in project.task_ids:
                    if task.user_id and task.user_id not in user_ids:
                        user_ids += task.user_id
                    for user_id in task.project_team_user_ids:
                        if user_id not in user_ids:
                            user_ids += user_id
                project.user_ids = user_ids
                project.user_ids_images = dumps([(x.id, x.name) for x in user_ids])
