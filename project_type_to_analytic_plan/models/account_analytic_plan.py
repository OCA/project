# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountAnalyticPlan(models.Model):
    _inherit = "account.analytic.plan"

    project_type_id = fields.Many2one(
        comodel_name="project.type",
        string="Project Type",
        help="The project type this plan is linked to",
    )

    def _is_under_root_plan(self, company=None):
        self.ensure_one()
        company = company or self.env.company
        root_plan = company.project_types_root_analytic_plan_id
        if not root_plan:
            return False
        if self.id == root_plan.id:
            return False
        if not self.parent_id:
            return False
        if self.parent_id.id == root_plan.id:
            return True
        return self.parent_id._is_under_root_plan(company)

    def write(self, vals):
        if not self.env.context.get("from_project_type_sync"):
            tracked = {"name", "parent_id"}
            if tracked & set(vals):
                for plan in self:
                    if plan._is_under_root_plan():
                        raise UserError(
                            _(
                                "You cannot modify analytic plans that are "
                                "synchronized with project types. Please modify "
                                "the project type instead."
                            )
                        )
        return super().write(vals)

    def unlink(self):
        for plan in self:
            if plan._is_under_root_plan() and plan.account_count > 0:
                raise UserError(
                    _(
                        "You cannot delete this analytic plan because it "
                        "contains analytic accounts. Delete the accounts first "
                        "or remove the project type association."
                    )
                )
        return super().unlink()
