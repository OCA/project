# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class HrHolidaysPublicLine(models.Model):
    _inherit = "hr.holidays.public.line"

    @api.model_create_multi
    def create(self, values):
        records = super().create(values)
        # TODO: only recompute if one of the created line is a public holiday
        # in the horizon
        self.env["forecast.line"].sudo()._cron_recompute_all()
        return records
