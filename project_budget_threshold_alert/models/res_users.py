# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"
    receive_budget_threshold_notification = fields.Boolean(
        string="Notify me if the project budget exceeds the threshold", default=True
    )
