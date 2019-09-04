# Copyright 2019 Praxya - Juan Carlos Montoya
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.multi
    def _timesheet_postprocess(self, values):
        if self._context.get('norecompute_amount'):
            return values
        else:
            return super(AccountAnalyticLine, self)._timesheet_postprocess(
                values)
