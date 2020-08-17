# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    project_user_id = fields.Many2one('res.users',
                                      related='task_id.project_id.user_id',
                                      string='Project Manager',
                                      store=True,
                                      readonly=True)
    is_manager = fields.Boolean('Is Manager?',
                                compute='_compute_is_manager',
                                store=True)

    @api.depends('employee_id', 'project_user_id')
    def _compute_is_manager(self):
        for rec in self:
            if rec.employee_id.user_id == rec.project_user_id:
                rec.is_manager = True
