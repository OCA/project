# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ProjectProject(models.Model):
    _inherit = "project.project"

    template_id = fields.Many2one(
        "project.project",
        string="Created From Template",
        copy=False,
        readonly=True,
    )
    template_child_ids = fields.One2many(
        "project.project", "template_id", string="Linked Projects", copy=False
    )

    def _get_root_template(self):
        self.ensure_one()
        return self.template_id or self

    def _apply_stage_order_from(self, source_project):
        self.ensure_one()
        if not self.env.company.task_stage_order_enabled:
            return
        Sequence = self.env["project.task.type.sequence"]
        source_rows = Sequence.search([("project_id", "=", source_project.id)])
        for row in source_rows:
            target_row = Sequence.search(
                [
                    ("project_id", "=", self.id),
                    ("stage_id", "=", row.stage_id.id),
                ],
                limit=1,
            )
            if target_row:
                target_row.with_context(template_propagate=True).write(
                    {"sequence": row.sequence}
                )

    def action_open_template_copy_wizard(self):
        self.ensure_one()
        return {
            "name": "Create Copy",
            "type": "ir.actions.act_window",
            "res_model": "project.template.copy.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_template_id": self.id,
                "default_name": self.name,
            },
        }

    def action_open_link_template_wizard(self):
        self.ensure_one()
        return {
            "name": "Link to Another Project",
            "type": "ir.actions.act_window",
            "res_model": "project.link.template.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_project_id": self.id},
        }

    def action_unlink_from_template(self):
        self.ensure_one()
        self.template_id = False

    @api.constrains("is_template", "template_id")
    def _check_linked_project_not_template(self):
        for project in self:
            if (
                project.is_template
                and project.template_id
                and project.env.company.task_stage_order_enabled
            ):
                raise ValidationError(
                    _(
                        'You cannot mark "%(project)s" as a template because '
                        'it is linked to the template "%(template)s". Go to '
                        "that project to create a new linked copy instead.",
                        project=project.name,
                        template=project.template_id.name,
                    )
                )

    def write(self, values):
        if (
            "type_ids" in values
            and not self.env.context.get("template_propagate")
            and self.env.company.task_stage_order_enabled
        ):
            for project in self:
                if project.template_id:
                    raise UserError(
                        _(
                            'You cannot change the stages of "%(project)s" '
                            'because it follows the template "%(template)s". '
                            "Change the stages on the template instead.",
                            project=project.name,
                            template=project.template_id.name,
                        )
                    )
        result = super().write(values)
        if "type_ids" in values and self.env.company.task_stage_order_enabled:
            for project in self:
                children = project.template_child_ids
                if not children:
                    continue
                children.with_context(template_propagate=True).write(
                    {"type_ids": [(6, 0, project.type_ids.ids)]}
                )
        return result

    def unlink(self):
        for project in self:
            if project.template_child_ids:
                raise UserError(
                    _(
                        'You cannot delete "%(project)s" because it has '
                        "projects linked to it as a template. Delete those "
                        "projects first: %(children)s",
                        project=project.name,
                        children=", ".join(project.template_child_ids.mapped("name")),
                    )
                )
        return super().unlink()

    # OVERRIDE: don't auto-append "(TEMPLATE)"/"(COPY)" to the name anymore,
    # the wizard asks for the name directly instead.
    @api.onchange("is_template")
    def on_change_is_template(self):
        if self.is_template:
            if self.template_id and self.env.company.task_stage_order_enabled:
                self.is_template = False
                raise UserError(
                    _(
                        'You cannot mark "%(project)s" as a template because '
                        'it is linked to the template "%(template)s". Go to '
                        "that project to create a new linked copy instead.",
                        project=self.name,
                        template=self.template_id.name,
                    )
                )
            if self.user_id:
                self.user_id = False
            if self.partner_id:
                self.partner_id = False
            if self.alias_name:
                self.alias_name = False
