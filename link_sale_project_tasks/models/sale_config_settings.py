# -*- coding: utf-8 -*-

# © 2017 Le Filament (<http://www.le-filament.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    project_task_type_id = fields.Many2one(
        'project.task.type', 'Initial step')

    @api.multi
    def set_project_task_type(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings',
            'project_task_type_id',
            self.project_task_type_id.id
            )
