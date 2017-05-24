# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _get_timesheet_cost(self, values):
        res = super(AccountAnalyticLine, self)._get_timesheet_cost(values)
        project_id = values.get('project_id')
        if project_id and res.get('amount'):
            project_model = self.env['project.project']
            project = project_model.browse(project_id)
            currency = project.currency_id
            base_currency = self.env.user.company_id.currency_id
            res['amount_currency'] = res['amount']
            res['amount'] = currency.compute(res['amount'], base_currency)
        return res
