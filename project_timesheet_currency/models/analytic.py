# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _get_timesheet_cost(self, values):
        project_id = values.get('project_id', False)
        if project_id:
            project_model = self.env['project.project']
            project = project_model.browse(project_id)
            currency = project.currency_id
            import ipdb;ipdb.set_trace()
        return super(AccountAnalyticLine, self)._get_timesheet_cost(values)
