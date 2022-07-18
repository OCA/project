# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        recs.mapped("task_id")._update_forecast_lines()
        return recs

    def write(self, values):
        res = super().write(values)
        self.mapped("task_id")._update_forecast_lines()
        return res
