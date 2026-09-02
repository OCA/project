# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    project_margin_threshold = fields.Float(
        config_parameter="project_margin_threshold_alert.project_margin_threshold",
        help="Check this to define a default margin",
    )
    project_margin_threshold_send_email = fields.Boolean(
        config_parameter="project_margin_threshold_alert.project_margin_threshold_send_email",
        help="Check this to enable by default the sending of emails"
        "to internal users when project margin is exceeded.",
    )
    project_margin_threshold_create_activity = fields.Boolean(
        config_parameter="project_margin_threshold_alert.project_margin_threshold_create_activity",
        help="Check this to enable by default the creation of activity"
        "for dedicated project manager when project margin threshold (minimum) is .",
    )
