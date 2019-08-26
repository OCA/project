# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_project_required = fields.Boolean(
        string='Is Project Required',
        related='company_id.is_project_task_project_required',
    )

    @api.constrains('project_id')
    def _check_project_id(self):
        for task in self:
            if task.is_project_required and not task.project_id:
                raise ValidationError(_(
                    'You must specify a project for the task.'
                ))
