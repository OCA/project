# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _is_move_allowed(self, task, new_stage, user):
        """Return True if **user** may move **task** into **new_stage** (OR-logic).

        OR-logic sequence:
        1. No restrictions on stage, or superuser → always True
        2. allow_assigned_only and user in task.user_ids
        3. allow_project_manager and user is project.manager_id
        4. allow_group_ids and user in allowed groups
        """
        # unrestricted stage / super-user
        if not new_stage or not new_stage._has_restrictions() or user._is_superuser():
            return True

        # Assigned Only
        if new_stage.allow_assigned_only and user in task.user_ids:
            return True

        # Project Manager: use the core alias `manager_id`
        pm = getattr(task.project_id, "manager_id", task.project_id.user_id)
        if new_stage.allow_project_manager and pm and user == pm:
            return True

        # Group Members
        if new_stage._user_in_allowed_group(user):
            return True

        return False

    def _check_stage_restriction(self, vals):
        """Raise UserError if current env-user is NOT allowed."""
        stage_id = vals.get("stage_id")
        if not stage_id:
            return True

        new_stage = self.env["project.task.type"].browse(stage_id)
        if not new_stage:
            return True

        for task in self:
            if not self._is_move_allowed(task, new_stage, self.env.user):
                raise UserError(
                    _(
                        "Sorry, you are not allowed to move the task "
                        "'%(task)s' into the stage '%(stage)s'."
                    )
                    % {"task": task.display_name, "stage": new_stage.display_name}
                )
        return True

    def write(self, vals):
        """Override write() to enforce stage‐change restrictions."""
        # validate the user is allowed to move into a new stage
        self._check_stage_restriction(vals)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create() to enforce stage restrictions on new tasks.

        :param vals_list: list of dicts of values for each record
        :return: the newly created recordset
        """
        recs = super().create(vals_list)
        # validate once stage is definitely set
        for rec in recs:
            if rec.stage_id:
                rec._check_stage_restriction({"stage_id": rec.stage_id.id})
        return recs
