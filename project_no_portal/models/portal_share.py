# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.exceptions import UserError

BLOCKED_MODELS = ("project.project", "project.task")


class PortalShare(models.TransientModel):
    _inherit = "portal.share"

    @api.model
    def default_get(self, fields_list):
        # Guard every entrypoint to the share wizard (kanban link, cog action,
        # saved URL). The kanban "Share Task" link references the action by
        # xml-id, so removing the model binding does not hide it.
        res = super().default_get(fields_list)
        model = res.get("res_model") or self.env.context.get("active_model")
        res_id = res.get("res_id") or self.env.context.get("active_id")
        if not (res_id and model in BLOCKED_MODELS):
            return res

        record = self.env[model].browse(res_id)
        company = record._portal_block_company()
        if not company.block_project_portal_access:
            return res

        raise UserError(
            _(
                "Sharing is disabled for company %(company)s: portal users "
                "can not access its projects or tasks. An administrator can "
                "allow it in Settings > Project.",
                company=company.display_name,
            )
        )
