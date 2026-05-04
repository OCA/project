# Copyright 2025 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command, api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        for task in tasks:
            default_users, mode = task._get_default_users_and_mode()
            if default_users:
                task._apply_default_users(default_users, mode)

        return tasks

    def write(self, vals):
        res = super().write(vals)
        if "stage_id" in vals:
            for task in self:
                default_users, mode = task._get_default_users_and_mode()
                if default_users:
                    task._apply_default_users(default_users, mode)

        return res

    def _get_default_users_and_mode(self):
        self.ensure_one()
        if self.stage_id and self.stage_id.default_user_ids:
            return (
                self.stage_id.default_user_ids.ids,
                self.stage_id.stage_task_assignment_mode or "replace",
            )

        if self.project_id and self.project_id.default_user_ids:
            return (
                self.project_id.default_user_ids.ids,
                self.project_id.project_task_assignment_mode or "replace",
            )

        return None, "replace"

    def _apply_default_users(self, default_users, mode):
        self.ensure_one()
        if mode == "merge":
            existing = self.user_ids.ids or []
            merged = list(dict.fromkeys(existing + default_users))
            self.user_ids = [Command.set(merged)]
        else:
            self.user_ids = [Command.set(default_users)]
