# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    critical_path_duration_base = fields.Selection(
        string='Base project critical path on',
        default='date',
        selection=[
            ('date', 'Start and end date'),
            ('planned_hours', 'Initially planned hours')
        ]
    )
