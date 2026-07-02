# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    block_project_portal_access = fields.Boolean(
        string="Block portal access to projects and tasks",
        default=False,
        help="When enabled, portal users of this company cannot read its "
        "projects or tasks, and portal visibility cannot be set on them.",
    )

    def write(self, vals):
        res = super().write(vals)
        if "block_project_portal_access" in vals:
            if vals["block_project_portal_access"]:
                self.env["project.project"]._disable_portal_visibility(self)
            self._sync_share_actions()
        return res

    def _sync_share_actions(self):
        """Re-enable the share actions when at least one company allows portal."""
        enabled = bool(
            self.sudo().search_count(
                [("block_project_portal_access", "=", False)], limit=1
            )
        )
        self.env["project.task"]._set_share_task_action(enabled)
        self.env["project.project"]._set_share_project_action(enabled)
