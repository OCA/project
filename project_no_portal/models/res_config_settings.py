# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    block_project_portal_access = fields.Boolean(
        related="company_id.block_project_portal_access",
        readonly=False,
        string="Block portal access to projects and tasks",
        help="When enabled, portal users of the selected company cannot read "
        "its projects or tasks, and portal visibility cannot be set on them.",
    )
