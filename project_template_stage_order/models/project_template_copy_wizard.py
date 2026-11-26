# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models

from odoo.addons.project_template.models.project import TASK_DEFAULT_COPY_CONTEXT_KEY


class ProjectTemplateCopyWizard(models.TransientModel):
    _name = "project.template.copy.wizard"
    _description = "Create a Copy From a Project Template"

    template_id = fields.Many2one("project.project", required=True)
    name = fields.Char(required=True)
    link_to_template = fields.Boolean(
        string="Keep linked to the template",
        help="If checked, this copy will follow the template: its task "
        "stages can only be changed from the template, and changes there "
        "will apply here too.",
    )

    def action_confirm(self):
        self.ensure_one()
        default = {
            "name": self.name,
            "active": True,
            "alias_name": False,
            "task_ids": [],
            "tasks": False,
        }
        if self.link_to_template:
            default["template_id"] = self.template_id._get_root_template().id
        clean_context = {
            key: value
            for key, value in self.env.context.items()
            if not key.startswith("default_")
        }
        new_project = self.template_id.with_context(
            clean_context, **{TASK_DEFAULT_COPY_CONTEXT_KEY: True}
        ).copy(default=default)
        new_project._apply_stage_order_from(self.template_id)
        return {
            "view_mode": "form",
            "res_model": "project.project",
            "target": "current",
            "res_id": new_project.id,
            "type": "ir.actions.act_window",
        }
