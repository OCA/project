# Copyright (C) 2019 - TODAY, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    project_id = fields.Many2one('project.project', string='Project',
                                 track_visibility='onchange')
    project_task_id = fields.Many2one('project.task', string='Project Task',
                                      track_visibility='onchange')
