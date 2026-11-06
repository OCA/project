# Copyright 2026 Cyril VINH-TUNG (INVITU) <cyril@invitu.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProjectTaskMerge(models.TransientModel):
    _inherit = "project.task.merge"

    def merge_tasks(self):
        original_task_ids = self.task_ids
        result = super().merge_tasks()
        merged_tasks = original_task_ids - self.dst_task_id
        self._merge_dependences_timesheets(merged_tasks)
        return result

    def _merge_dependences_timesheets(self, merged_tasks):
        timesheet_ids = merged_tasks.sudo().timesheet_ids
        if timesheet_ids:
            timesheet_ids.write({"task_id": self.dst_task_id.id})
