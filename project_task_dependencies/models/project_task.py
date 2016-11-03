# -*- coding: utf-8 -*-
# © 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_ids = fields.Many2many(
        comodel_name='project.task', relation='project_task_project_task_rel',
        column1='task_id', column2='dependent_task_id', string='Dependencies',
    )
