# -*- coding: utf-8 -*-
# © 2017 Le Filament (<http://www.le-filament.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _get_type_common(self):
        ids = self.env['project.task.type'].search([
            ('case_default', '=', True)
            ])
        return ids

    type_ids = fields.Many2many(
        comodel_name='project.task.type', relation='project_task_type_rel',
        column1='project_id', column2='type_id', string='Tasks Stages',
        default=_get_type_common
    )
