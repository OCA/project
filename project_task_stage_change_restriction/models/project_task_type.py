# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    allow_assigned_only = fields.Boolean(string="Assigned Only")
    allow_project_manager = fields.Boolean(string="Project Manager")
    allow_group_ids = fields.Many2many(
        "res.groups",
        "project_task_stage_allowed_group_rel",
        "stage_id",
        "group_id",
        string="Group Members",
    )

    def _has_restrictions(self):
        """Return *True* if **any** restriction flag / group is set."""
        self.ensure_one()
        return bool(
            self.allow_assigned_only
            or self.allow_project_manager
            or self.allow_group_ids
        )

    def _user_in_allowed_group(self, user):
        """
        Return *True* when *user* belongs to ≥ 1 selected groups.
        Empty group list → rule **not** applied.
        """
        self.ensure_one()
        if not self.allow_group_ids:
            return False
        return bool(self.allow_group_ids & user.groups_id)
