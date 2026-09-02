# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    receive_project_margin_threshold_notification = fields.Boolean(
        string="Activate minimum margin notifications for projects",
        help="Notify user about project minimum margin threshold exceeding",
        default=True,
    )
