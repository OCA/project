# Copyright 2023 - Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    description_template_id = fields.Many2one(
        "project.task.description.template",
        domain="['|', ('project_ids', '=', False), ('project_ids', 'in', project_id)]",
    )
    portal_description_template_required = fields.Boolean(
        related="project_id.portal_task_description_template_required"
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS | {"portal_description_template_required"}

    @property
    def SELF_WRITABLE_FIELDS(self):
        return super().SELF_WRITABLE_FIELDS | {"description_template_id"}

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        if self.env.user._is_portal():
            tasks._check_portal_description_template()
        return tasks

    def write(self, vals):
        res = super().write(vals)
        if "description_template_id" in vals and self.env.user._is_portal():
            self._check_portal_description_template(check_required=False)
        return res

    def _check_portal_description_template(self, check_required=True):
        for task in self:
            template = task.description_template_id.sudo()
            project = task.project_id.sudo()
            if template and project not in template.project_ids:
                raise ValidationError(
                    self.env._(
                        "The description template %(template)s is not available "
                        "in project %(project)s.",
                        template=template.display_name,
                        project=project.display_name,
                    )
                )
            if (
                check_required
                and not template
                and not task.parent_id
                and task.portal_description_template_required
            ):
                raise ValidationError(
                    self.env._(
                        "A description template is required to create tasks "
                        "in project %(project)s.",
                        project=project.display_name,
                    )
                )

    @api.onchange("description_template_id")
    def _onchange_description_template_id(self):
        if self.description_template_id:
            description = self.description if self.description else ""
            self.description = description + self.description_template_id.description
