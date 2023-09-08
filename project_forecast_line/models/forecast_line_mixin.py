# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ForecastLineModelMixin(models.AbstractModel):
    _name = "forecast.line.mixin"
    _description = "mixin for models which generate forecast lines"

    def _get_forecast_lines(self, domain=None):
        self.ensure_one()
        base_domain = [("res.model", "=", self._name), ("res_id", "=", self.id)]
        if domain is not None:
            base_domain += domain
        return self.env["forecast.line"].search(base_domain)

    @api.model
    def _recompute_forecast_lines(self, force_company_id=None):
        return super()._recompute_forecast_lines(force_company_id=force_company_id)

    def _update_forecast_lines(self, **kwargs):
        return super()._update_forecast_lines(**kwargs)
