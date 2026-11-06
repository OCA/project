# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = "project.project"

    task_description_template_ids = fields.Many2many(
        "project.task.description.template",
        "project_task_description_template_project_rel",
        "project_id",
        "template_id",
        string="Task Description Templates",
        help="Templates available for the tasks of this project. Templates "
        "without projects are also available for internal users.",
    )
    portal_task_description_template_required = fields.Boolean(
        string="Require Description Template on Portal Tasks",
    )

    @api.constrains(
        "privacy_visibility",
        "portal_task_description_template_required",
        "task_description_template_ids",
    )
    def _check_portal_task_description_template_required(self):
        for project in self:
            if (
                project.privacy_visibility == "portal"
                and project.portal_task_description_template_required
                and not project.task_description_template_ids
            ):
                raise ValidationError(
                    self.env._(
                        "Project %(project)s requires a description template on "
                        "portal tasks, so it must have at least one template.",
                        project=project.display_name,
                    )
                )
