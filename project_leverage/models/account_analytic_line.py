# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    project_user_id = fields.Many2one('res.users',
                                      string='Project Manager',
                                      store=True,
                                      readonly=True)

    @api.depends('employee_id', 'project_user_id')
    def _compute_is_manager(self):
        for rec in self:
            if rec.employee_id.user_id == rec.project_user_id:
                rec.is_manager = True

    @api.model
    def create(self, vals):
        project_user_id = vals.get('task_id', False).project_id.user_id
        vals.update({'project_user_id': project_user_id})
        return super(AccountAnalyticLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('task_id', False):
            project_user_id = vals.get('task_id', False).project_id.user_id
            vals.update({'project_user_id': project_user_id})
        return super(AccountAnalyticLine, self).write(vals)
