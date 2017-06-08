# -*- coding: utf-8 -*-
# © 2011 Joël Grand-Guillaume (Camptocamp SA)
# © 2013 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    department_id = fields.Many2one(
        'hr.department',
        'Department')


class AnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.multi
    def _get_department(self):
        emp_model = self.env['hr.employee']
        department_id = False
        employee = emp_model.search([('user_id', '=', self.env.uid)], limit=1)
        if employee and employee.department_id:
            department_id = employee.department_id.id
        return department_id

    department_id = fields.Many2one(
        'hr.department',
        'Department',
        default=_get_department,
        help="User's related department")
    account_department_id = fields.Many2one(
        comodel_name='hr.department',
        related='account_id.department_id',
        string='Account Department',
        store=True,
        readonly=True,
        help="Account's related department")
