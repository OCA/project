# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"
    receive_project_threshold_notification = fields.Boolean(
        string="Activate notifications for projects",
        help="Notify user about project costs threshold exceeding",
        default=True,
    )
