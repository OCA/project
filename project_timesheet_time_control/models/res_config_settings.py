from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    timesheet_alignment = fields.Selection(
        selection=[
            ("now", "Set Start Date to Now"),
            ("no-gap", "Align to previous entry"),
        ],
        default="now",
        config_parameter="project_timesheet_time_control.timesheet_alignment",
        help="Choose the alignment of new timesheet entries without start time.",
    )
