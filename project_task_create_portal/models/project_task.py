from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class ProjectTask(models.Model):
    _inherit = "project.task"

    portal_stage_editable = fields.Boolean(
        compute="_compute_portal_stage_editable",
        store=True,
    )

    @api.depends("project_id.portal_stage_id", "stage_id")
    def _compute_portal_stage_editable(self):
        """Compute whether each task is in its project's portal stage."""
        for task in self:
            task.portal_stage_editable = bool(
                task.project_id.portal_stage_id
                and task.stage_id == task.project_id.portal_stage_id
            )

    @api.model
    def _check_portal_fields_access(self):
        """Return fields that portal users may create or edit."""
        return ["name", "description", "date_deadline"]

    @property
    def SELF_WRITABLE_FIELDS(self):
        """Extend Odoo's portal-writable fields with this module's fields."""
        return super().SELF_WRITABLE_FIELDS | set(self._check_portal_fields_access())

    def check_portal_edit_access(self):
        """Check if the current user has portal access to edit this task."""
        # Portal users can only access tasks in projects with portal task creation enabled
        self.ensure_one()
        if not self.project_id.is_portal_task_creation_allowed():
            return False

        # Portal users can only access tasks in the allowed stage
        if self.stage_id != self.project_id.portal_stage_id:
            return False

        # Portal users can only edit their own tasks
        if self.create_uid.id != self.env.context.get("uid", self.env.user.id):
            return False
        return True

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle portal user restrictions."""
        if self.env.su or not self.env.user.has_group("base.group_portal"):
            return super().create(vals_list)

        self.check_access_rights("create")
        allowed_fields = set(self._check_portal_fields_access()) | {"project_id"}
        records = self.sudo().browse()
        for create_vals in vals_list:
            vals = dict(create_vals)
            vals.pop("user_ids", None)
            forbidden_fields = set(vals) - allowed_fields
            if forbidden_fields:
                raise AccessError(
                    _("Portal users cannot set the following task fields: %s")
                    % ", ".join(sorted(forbidden_fields))
                )
            project = self.env["project.project"].sudo().browse(vals.get("project_id"))
            if not project.exists() or not project.is_portal_task_creation_allowed():
                raise AccessError(
                    _("You are not allowed to create tasks in this project.")
                )
            vals.pop("project_id")
            vals.update(
                stage_id=project.portal_stage_id.id,
                partner_id=self.env.user.partner_id.id,
            )
            task_model = self.with_context(
                default_project_id=project.id,
                default_user_ids=False,
            )
            # Other task modules may add or write protected fields in create hooks.
            # Keep their chain in sudo and explicitly validate the final record rule.
            record = super(ProjectTask, task_model.sudo()).create([vals])
            record.with_user(self.env.user).check_access_rule("create")
            records |= record
        return records

    def write(self, vals):
        """Override write to handle portal user restrictions."""
        if self.env.user.has_group("base.group_portal") and not self.env.su:
            forbidden_fields = set(vals) - set(self._check_portal_fields_access())
            if forbidden_fields:
                raise AccessError(
                    _("Portal users cannot edit the following task fields: %s")
                    % ", ".join(sorted(forbidden_fields))
                )
            if any(not task.check_portal_edit_access() for task in self):
                raise AccessError(
                    _("You are not allowed to edit tasks in this project.")
                )
        return super().write(vals)
