from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = "project.project"

    portal_stage_id = fields.Many2one(
        "project.task.type",
        help="Stage from which portal users will be allowed to create and edit tasks.",
        domain="[('project_ids', 'in', [id])]",
    )
    portal_user_ids = fields.Many2many(
        "res.users",
        relation="portal_project_allowed_user_rel",
        column1="project_id",
        column2="user_id",
        domain=lambda self: [
            ("groups_id", "in", self.env.ref("base.group_portal").ids)
        ],
    )
    portal_hide_assigned_users = fields.Boolean(
        string="Hide Assigned User",
        help="If enabled, the portal assigned users will not be displayed in the project.",
    )

    @api.constrains("portal_stage_id")
    def _check_portal_stage_id(self):
        """Ensure the portal task creation stage belongs to this project."""
        for project in self:
            stage = project.portal_stage_id
            if stage and stage not in project.type_ids:
                raise ValidationError(
                    _("The Portal Task Creation Stage must belong to this project.")
                )

    def is_portal_task_creation_allowed(self):
        """Check if portal task creation is allowed for this project."""
        self.ensure_one()
        return (
            bool(self.portal_stage_id)
            and self.env.context.get("uid", self.env.user.id)
            in self.portal_user_ids.ids
        )
