from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model
    def get_unusual_days(self, date_from, date_to=None):
        return super().env["hr.leave"].get_unusual_days(date_from, date_to=date_to)
