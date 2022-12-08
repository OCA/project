# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ForecastLine(models.Model):
    _inherit = "forecast.line"

    def prepare_forecast_lines(self, *args, **kwargs):
        self = self.with_context(exclude_public_holidays=True)
        return super().prepare_forecast_lines(*args, **kwargs)

    def _cron_recompute_all(self, force_company_id=None, force_delete=False):
        self = self.with_context(exclude_public_holidays=True)
        return super()._cron_recompute_all(force_company_id, force_delete)
