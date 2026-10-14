# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    project_types_root_analytic_plan_id = fields.Many2one(
        comodel_name="account.analytic.plan",
        string="Root Analytic Plan for Project Types",
        related="company_id.project_types_root_analytic_plan_id",
        readonly=False,
        help="Root analytic plan used for synchronizing project types",
    )

    def action_synchronize_project_types_with_plans(self):
        self.ensure_one()

        if not self.project_types_root_analytic_plan_id:
            raise UserError(_("Please configure a Root Analytic Plan first."))

        root_plan = self.project_types_root_analytic_plan_id
        plans_to_delete = self.env["account.analytic.plan"].search(
            [
                ("parent_id", "child_of", root_plan.id),
                ("id", "!=", root_plan.id),
            ]
        )
        plans_to_delete.unlink()

        root_project_types = (
            self.env["project.type"]
            .with_context(active_test=False)
            .search([("parent_id", "=", False)])
        )

        for project_type in root_project_types:
            project_type._create_analytic_plan(
                root_plan,
                recursive=True,
                sync_projects=True,
            )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _(
                    "Project types have been synchronized with analytic plans."
                ),
                "type": "success",
                "sticky": False,
            },
        }
