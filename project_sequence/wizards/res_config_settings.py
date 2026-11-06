# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    project_display_name_pattern = fields.Char(
        config_parameter="project_sequence.display_name_pattern",
        default="%(sequence_code)s - %(name)s",
        help=(
            "Use %(sequence_code)s and %(name)s to include the sequence code "
            "and the name of the project in the display name."
        ),
    )
