# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    restrict_ticket_conversion = fields.Boolean(
        related="company_id.restrict_ticket_conversion",
        readonly=False,
        string="Restrict task-to-ticket conversion to portal projects",
        help="When enabled, only tasks whose project is visible to invited "
        "portal users can be converted into helpdesk tickets.",
    )
