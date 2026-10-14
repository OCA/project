# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProjectType(models.Model):
    _inherit = "project.type"

    analytic_plan_id = fields.Many2one(
        comodel_name="account.analytic.plan",
        string="Analytic Plan",
        help="The analytic plan linked to this project type "
        "(for the current company)",
        compute="_compute_analytic_plan_id",
    )

    @api.depends_context("company")
    def _compute_analytic_plan_id(self):
        plans = (
            self.env["account.analytic.plan"]
            .sudo()
            .search([("project_type_id", "in", self.ids)])
        )
        plan_by_type = {plan.project_type_id.id: plan for plan in plans}
        for project_type in self:
            project_type.analytic_plan_id = plan_by_type.get(project_type.id, False)

    @api.model_create_multi
    def create(self, vals_list):
        project_types = super().create(vals_list)
        for project_type in project_types:
            project_type._sync_analytic_plan_on_create()
        return project_types

    def write(self, vals):
        result = super().write(vals)
        if "name" in vals or "parent_id" in vals:
            self._sync_analytic_plan_on_write(vals)
        if "project_ok" in vals:
            self._sync_analytic_plan_on_project_ok_change(vals["project_ok"])
        return result

    def unlink(self):
        for project_type in self:
            project_count = self.env["project.project"].search_count(
                [("type_id", "=", project_type.id)]
            )
            if project_count > 0:
                raise UserError(
                    _(
                        "You cannot delete this project type because it has "
                        "%s project(s). Please remove or reassign the "
                        "projects first."
                    )
                    % project_count
                )

            if project_type.analytic_plan_id:
                if project_type.analytic_plan_id.account_count == 0:
                    project_type.analytic_plan_id.unlink()
                else:
                    raise UserError(
                        _(
                            "You cannot delete this project type because its "
                            "analytic plan contains %s analytic account(s)."
                        )
                        % project_type.analytic_plan_id.account_count
                    )

        return super().unlink()

    def _sync_analytic_plan_on_create(self):
        self.ensure_one()

        if not self.project_ok:
            return

        root_plan = self.env.company.project_types_root_analytic_plan_id
        if not root_plan:
            return

        if self.parent_id and self.parent_id.analytic_plan_id:
            parent_plan = self.parent_id.analytic_plan_id
        else:
            parent_plan = root_plan

        self._create_analytic_plan(parent_plan)

    def _create_analytic_plan(self, parent_plan, recursive=False, sync_projects=False):
        self.ensure_one()

        plan = (
            self.env["account.analytic.plan"]
            .sudo()
            .create(
                {
                    "name": self.name,
                    "parent_id": parent_plan.id,
                    "project_type_id": self.id,
                }
            )
        )

        if sync_projects:
            projects = (
                self.env["project.project"]
                .with_context(active_test=False)
                .search([("type_id", "=", self.id)])
            )
            for project in projects:
                if project.account_id:
                    project.account_id.with_context(from_project_sync=True).write(
                        {"plan_id": plan.id}
                    )

        if recursive:
            child_types = self.with_context(active_test=False).child_ids
            for child_type in child_types:
                child_type._create_analytic_plan(
                    plan, recursive=True, sync_projects=sync_projects
                )

        return plan

    def _sync_analytic_plan_on_write(self, vals):
        for project_type in self:
            if not project_type.analytic_plan_id:
                continue

            if "name" in vals:
                project_type.analytic_plan_id.with_context(
                    from_project_type_sync=True
                ).write({"name": vals["name"]})

            if "parent_id" in vals:
                if vals["parent_id"]:
                    parent_type = self.env["project.type"].browse(vals["parent_id"])
                    if parent_type.analytic_plan_id:
                        project_type.analytic_plan_id.with_context(
                            from_project_type_sync=True
                        ).write({"parent_id": parent_type.analytic_plan_id.id})
                else:
                    root_plan = self.env.company.project_types_root_analytic_plan_id
                    if root_plan:
                        project_type.analytic_plan_id.with_context(
                            from_project_type_sync=True
                        ).write({"parent_id": root_plan.id})

    def _sync_analytic_plan_on_project_ok_change(self, project_ok):
        for project_type in self:
            if project_ok:
                if not project_type.analytic_plan_id:
                    root_plan = self.env.company.project_types_root_analytic_plan_id
                    if root_plan:
                        if (
                            project_type.parent_id
                            and project_type.parent_id.analytic_plan_id
                        ):
                            parent_plan = project_type.parent_id.analytic_plan_id
                        else:
                            parent_plan = root_plan
                        project_type._create_analytic_plan(
                            parent_plan, sync_projects=True
                        )
            else:
                if project_type.analytic_plan_id:
                    if project_type.analytic_plan_id.account_count == 0:
                        project_type.analytic_plan_id.unlink()
                    else:
                        raise UserError(
                            _(
                                'Cannot disable "Can be applied for projects" '
                                'because the analytic plan "%(name)s" contains '
                                "%(count)s analytic account(s)."
                            )
                            % {
                                "name": project_type.analytic_plan_id.name,
                                "count": project_type.analytic_plan_id.account_count,
                            }
                        )
