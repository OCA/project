# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        projects._link_analytic_account_to_plan()
        return projects

    def write(self, vals):
        result = super().write(vals)
        if "type_id" in vals or "account_id" in vals:
            self._link_analytic_account_to_plan()
        return result

    def _link_analytic_account_to_plan(self):
        for project in self:
            if (
                project.account_id
                and project.type_id
                and project.type_id.analytic_plan_id
            ):
                project.account_id.with_context(from_project_sync=True).write(
                    {"plan_id": project.type_id.analytic_plan_id.id}
                )
