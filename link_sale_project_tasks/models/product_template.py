# -*- coding: utf-8 -*-

# © 2017 Le Filament (<http://www.le-filament.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    project_task_type_id = fields.Many2one(
        'project.task.type', 'Project task stage')
    track_service = fields.Selection(selection_add=[
        ('project', 'Create a project and link tasks')])
