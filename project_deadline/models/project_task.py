# Copyright 2019 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    project_date_start = fields.Date(
        'Project Start Date',
        related='project_id.date_start'
    )

    project_date_deadline = fields.Date(
        'Project Deadline',
        related='project_id.date'
    )
