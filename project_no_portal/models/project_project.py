# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ProjectProject(models.Model):
    _name = "project.project"
    _inherit = ["project.project", "project.portal.block.mixin"]

    privacy_visibility = fields.Selection(
        default=lambda self: self._default_privacy_visibility()
    )

    @api.model
    def _disable_portal_visibility(self, companies):
        """Switch portal-visible projects of ``companies`` to employees.

        Done before the constraint can reject later writes when a company
        starts blocking portal access.
        """
        projects = self.search(
            [
                ("company_id", "in", companies.ids),
                ("privacy_visibility", "=", "portal"),
            ]
        )
        if projects:
            projects.write({"privacy_visibility": "employees"})
        return projects

    def _default_privacy_visibility(self):
        # Core defaults to "portal"; avoid clashing with the constraint when the
        # current company blocks portal access.
        if self.env.company.block_project_portal_access:
            return "employees"
        return "portal"

    @api.constrains("privacy_visibility", "company_id")
    def _check_no_portal_visibility(self):
        for project in self:
            company = project._portal_block_company()
            if (
                company.block_project_portal_access
                and project.privacy_visibility == "portal"
            ):
                raise ValidationError(
                    _(
                        "Portal visibility is disabled for company %(company)s: "
                        "portal users can not access its projects or tasks.",
                        company=company.display_name,
                    )
                )

    def action_open_share_project_wizard(self):
        self.ensure_one()
        for project in self:
            company = project._portal_block_company()
            if company.block_project_portal_access:
                raise UserError(
                    _(
                        "Sharing is disabled for company %(company)s: portal users "
                        "can not access its projects or tasks. An administrator can "
                        "allow it in Settings > Project.",
                        company=company.display_name,
                    )
                )
            return super().action_open_share_project_wizard()

    def _set_share_project_action(self, enabled):
        """Toggle the "Share Project" action"""
        action = self.env.ref(
            "project.project_share_wizard_action", raise_if_not_found=False
        )
        if not action:
            return
        model = self.env.ref("project.model_project_project")
        action.binding_model_id = model.id if enabled else False
