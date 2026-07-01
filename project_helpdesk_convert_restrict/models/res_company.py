# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    restrict_ticket_conversion = fields.Boolean(
        string="Restrict task-to-ticket conversion to portal projects",
        default=False,
        help="When enabled, only tasks whose project is visible to invited "
        "portal users can be converted into helpdesk tickets.",
    )
