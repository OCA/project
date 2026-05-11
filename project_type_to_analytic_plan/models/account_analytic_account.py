# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    def _is_under_root_plan(self):
        self.ensure_one()
        if not self.plan_id:
            return False
        root_plan = self.env.company.project_types_root_analytic_plan_id
        if not root_plan:
            return False
        if self.plan_id.id == root_plan.id:
            return True
        return self.plan_id._is_under_root_plan()

    def write(self, vals):
        if not self.env.context.get("from_project_sync"):
            if "plan_id" in vals:
                for account in self:
                    if account._is_under_root_plan():
                        raise UserError(
                            _(
                                "You cannot modify the analytic plan of "
                                "accounts that are linked to project types. "
                                "The plan is automatically managed."
                            )
                        )
        return super().write(vals)

    def unlink(self):
        for account in self:
            if account._is_under_root_plan():
                raise UserError(
                    _(
                        "You cannot delete analytic accounts that are linked "
                        "to project types. Delete the project first."
                    )
                )
        return super().unlink()
