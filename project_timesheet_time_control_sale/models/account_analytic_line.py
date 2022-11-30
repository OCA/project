# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2022 bosd
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    # _order = "date_time desc"

    @api.model
    def _running_domain(self):
        """Domain to find running timesheet lines."""
        return [
            ("date_time", "!=", False),
            ("user_id", "=", self.env.user.id),
            ("project_id.allow_timesheets", "=", True),
            ("unit_amount", "=", 0),
            ("timesheet_invoice_id", "=", False),  # include only uninvoiced lines
        ]
