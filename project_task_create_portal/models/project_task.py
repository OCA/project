from odoo import _, api, models
from odoo.exceptions import AccessError


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def _check_portal_fields_access(self):
        return ["name", "description", "date_deadline"]

    def check_portal_edit_access(self):
        """Check if the current user has portal access to edit this task."""
        # Portal users can only access tasks in projects with portal task creation enabled
        if not self.project_id.is_portal_task_creation_allowed():
            return False

        # Portal users can only access tasks in the allowed stage
        if self.stage_id != self.project_id.portal_stage_id:
            return False

        # Portal users can only edit their own tasks
        if self.create_uid != self.env.user:
            return False
        return True

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle portal user restrictions."""
        records = super().create(vals_list)
        if not self.env.user.has_group("base.group_portal"):
            return records
        for record in self:
            if not record.project_id.is_portal_task_creation_allowed():
                raise AccessError(
                    _("You are not allowed to create tasks in this project.")
                )
        records.write({"user_ids": [(6, 0, [])]})
        return records

    def write(self, vals):
        """Override write to handle portal user restrictions."""
        if (
            self.env.user.has_group("base.group_portal")
            and not self.check_portal_edit_access()
        ):
            raise AccessError(_("You are not allowed to edit tasks in this project."))
        return super().write(vals)
