# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    immediate_compute_forecast_line = fields.Boolean(
        related="company_id.immediate_compute_forecast_line", readonly=False
    )
