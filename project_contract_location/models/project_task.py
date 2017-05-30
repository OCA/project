# -*- coding: utf-8 -*-
# Copyright (C) 2013,2017 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import api, fields, models


class ProjectTask(models.Model):
    """
    Add related ``Analytic Account`` and service ``Location``.
    A Location can be any Contact Partner of the AA's Partner.
    """
    _inherit = 'project.task'
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        'Contract/Analytic',
        domain="[('account_type', '!=', 'closed')]")
    location_id = fields.Many2one(
        'res.partner',
        'Location',
        domain="[('parent_id', 'child_of', partner_id)]")
    use_analytic_account = fields.Selection(
        related='project_id.use_analytic_account',
        string="Use Analytic Account")
    project_code = fields.Char(
        related='project_id.code',
        string="Project Code")

    @api.onchange('analytic_account_id')
    def onchange_analytic(self):
        aa = self.analytic_account_id
        self.partner_id = aa.partner_id
        self.location_id = aa.location_id
        if hasattr(self, 'department_id') and hasattr(aa, 'department_id'):
            self.department_id = aa.department_id
