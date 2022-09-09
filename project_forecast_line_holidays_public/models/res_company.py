# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    immediate_compute_forecast_line = fields.Boolean(
        string="Recompute forecast lines immediately",
        default=True,
        help="If checked will force forecast lines recomputation on public holidays creation.",
    )
