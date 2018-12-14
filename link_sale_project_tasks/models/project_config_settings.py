# -*- coding: utf-8 -*-

# © 2017 Le Filament (<http://www.le-filament.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProjectConfigSettings(models.TransientModel):
    _inherit = 'project.config.settings'

    daily_price = fields.Float('Day Price')
    alias_prefix = fields.Char('Alias prefix')
    hours_per_day = fields.Float(
        'Hours / Day',
        help="Time base for calculating the number of hours "
        "sold per project (default 7h)",
        default=7.0
        )

    @api.multi
    def set_default_generate_project_alias(self):
        Values = self.env['ir.values'].sudo() or self.env['ir.values']
        for config in self:
            Values.set_default(
                'project.config.settings',
                'generate_project_alias',
                config.generate_project_alias
                )

    @api.multi
    def set_default_daily_price(self):
        return self.env['ir.values'].sudo().set_default(
            'project.config.settings', 'daily_price', self.daily_price)

    @api.multi
    def set_default_alias_prefix(self):
        return self.env['ir.values'].sudo().set_default(
            'project.config.settings', 'alias_prefix', self.alias_prefix)

    @api.multi
    def set_default_hours_per_day(self):
        return self.env['ir.values'].sudo().set_default(
            'project.config.settings', 'hours_per_day', self.hours_per_day)

    @api.multi
    def get_default_hours_per_day(self, field):
        hours_per_day = self.env['ir.values'].get_default(
            'project.config.settings',
            'hours_per_day'
            )
        return {'hours_per_day': hours_per_day or 7.0}
