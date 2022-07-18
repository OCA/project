# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class CapacityLine(models.Model):
    _inherit = "capacity.line"

    def prepare_capacity_lines(self, *args, **kwargs):
        self = self.with_context(exclude_public_holidays=True)
        return super().prepare_capacity_lines(*args, **kwargs)

    def _cron_recompute_all(self, force_company_id=None):
        self = self.with_context(exclude_public_holidays=True)
        return super()._cron_recompute_all(force_company_id)
