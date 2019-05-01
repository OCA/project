# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    seniority_level_id = fields.Many2one(
        name='Seniority level', comodel_name='hr.employee.seniority.level'
    )
