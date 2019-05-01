# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class HrEmployeeSeniorityLevel(models.Model):

    _name = 'hr.employee.seniority.level'
    _description = 'Hr Employee Seniority Level'
    _order = 'sequence'

    sequence = fields.Integer(name="Sequence", required=True)
    code = fields.Char(name='Code', required=True)
    name = fields.Char(name='Name', required=True, translate=True)
