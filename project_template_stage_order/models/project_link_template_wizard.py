# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, fields, models
from odoo.exceptions import UserError


class ProjectLinkTemplateWizard(models.TransientModel):
    _name = "project.link.template.wizard"
    _description = "Link an Existing Project to Another as a Template"

    project_id = fields.Many2one(
        "project.project", required=True, string="Current Project"
    )
    template_id = fields.Many2one("project.project", string="Project")
    state = fields.Selection(
        [("select", "Select"), ("confirm", "Confirm")],
        default="select",
        required=True,
    )
    parent_order_display = fields.Text(string="New Order", readonly=True)
    child_order_display = fields.Text(string="Current Order", readonly=True)

    def action_check(self):
        self.ensure_one()
        if not self.env.company.task_stage_order_enabled:
            raise UserError(_("This feature is not enabled for your company."))
        if not self.template_id:
            raise UserError(_("Select a project to link to."))
        if self.template_id == self.project_id:
            raise UserError(_("You cannot link a project to itself."))
        if self.project_id.template_child_ids:
            raise UserError(
                _(
                    'You cannot link "%(project)s" to another project '
                    "because it already has projects linked to it as a "
                    "template.",
                    project=self.project_id.name,
                )
            )
        child_stage_ids = set(self.project_id.type_ids.ids)
        parent_stage_ids = set(self.template_id.type_ids.ids)
        if child_stage_ids != parent_stage_ids:
            raise UserError(
                _(
                    '"%(child)s" and "%(parent)s" do not have the same '
                    "stages, so they cannot be linked.",
                    child=self.project_id.name,
                    parent=self.template_id.name,
                )
            )
        Sequence = self.env["project.task.type.sequence"]
        parent_rows = Sequence.search([("project_id", "=", self.template_id.id)])
        child_rows = Sequence.search([("project_id", "=", self.project_id.id)])
        self.parent_order_display = "\n".join(parent_rows.mapped("stage_id.name"))
        self.child_order_display = "\n".join(child_rows.mapped("stage_id.name"))
        self.state = "confirm"
        return {
            "type": "ir.actions.act_window",
            "res_model": "project.link.template.wizard",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_confirm(self):
        self.ensure_one()
        self.project_id.template_id = self.template_id._get_root_template().id
        self.project_id._apply_stage_order_from(self.template_id)
        return {
            "view_mode": "form",
            "res_model": "project.project",
            "target": "current",
            "res_id": self.project_id.id,
            "type": "ir.actions.act_window",
        }
