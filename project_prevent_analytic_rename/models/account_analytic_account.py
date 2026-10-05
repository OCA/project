# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    def write(self, vals):
        if self.env.context.get("prevent_analytic_rename"):
            vals.pop("name", None)
        return super().write(vals)
