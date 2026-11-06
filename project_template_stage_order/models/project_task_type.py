# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    def _get_context_project(self):
        project_id = self.env.context.get("default_project_id")
        if not project_id or not self._is_order_feature_enabled():
            return self.env["project.project"]
        return self.env["project.project"].browse(project_id)

    def _ensure_not_linked_child(self):
        if self.env.context.get("template_propagate"):
            return
        project = self._get_context_project()
        if project and project.template_id:
            raise UserError(
                _(
                    'You cannot add or remove stages on "%(project)s" '
                    'because it follows the template "%(template)s". Change '
                    "the stages on the template instead.",
                    project=project.name,
                    template=project.template_id.name,
                )
            )

    @api.model_create_multi
    def create(self, values_list):
        stages = super().create(values_list)
        if self._is_order_feature_enabled() and not self.env.context.get(
            "template_propagate"
        ):
            linked_projects = stages.project_ids.filtered("template_id")
            if linked_projects:
                project = fields.first(linked_projects)
                raise UserError(
                    _(
                        'You cannot add stages on "%(project)s" because '
                        'it follows the template "%(template)s". Change the '
                        "stages on the template instead.",
                        project=project.name,
                        template=project.template_id.name,
                    )
                )
            templates_with_children = stages.project_ids.filtered("template_child_ids")
            for template in templates_with_children:
                new_children = template.template_child_ids - stages.project_ids
                stages.with_context(template_propagate=True).write(
                    {"project_ids": [(4, child.id) for child in new_children]}
                )
        return stages

    def write(self, values):
        enabled = self._is_order_feature_enabled()
        propagate = self.env.context.get("template_propagate")
        before_by_stage = {}
        if "project_ids" in values and enabled and not propagate:
            before_by_stage = {stage: stage.project_ids for stage in self}
        result = super().write(values)
        if before_by_stage:
            for stage, before_ids in before_by_stage.items():
                after_ids = stage.project_ids
                before_linked = before_ids.filtered("template_id")
                after_linked = after_ids.filtered("template_id")
                if before_linked != after_linked:
                    changed_project = fields.first(before_linked | after_linked)
                    raise UserError(
                        _(
                            'You cannot change the stages of "%(project)s" '
                            'because it follows the template "%(template)s". '
                            "Change the stages on the template instead.",
                            project=changed_project.name,
                            template=changed_project.template_id.name,
                        )
                    )
                added = (after_ids - before_ids).filtered("template_child_ids")
                removed = (before_ids - after_ids).filtered("template_child_ids")
                for template in added:
                    new_children = template.template_child_ids - after_ids
                    stage.with_context(template_propagate=True).write(
                        {"project_ids": [(4, child.id) for child in new_children]}
                    )
                for template in removed:
                    old_children = template.template_child_ids & before_ids
                    if old_children:
                        stage.with_context(template_propagate=True).write(
                            {"project_ids": [(3, child.id) for child in old_children]}
                        )
        return result

    def unlink(self):
        self._ensure_not_linked_child()
        project = self._get_context_project()
        if project and project.template_child_ids:
            for child in project.template_child_ids:
                stages_in_child = self.filtered(
                    lambda stage, child=child: child in stage.project_ids
                )
                stages_in_child.with_context(
                    default_project_id=child.id, template_propagate=True
                ).unlink()
        return super().unlink()
