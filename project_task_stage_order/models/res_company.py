# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    task_stage_order_enabled = fields.Boolean(
        string="Per-Project Task Stage Order",
        help="If activated, this company can give each of its projects "
        "an independent task stage order. If deactivated, all projects "
        "share the same task stage order.",
    )
