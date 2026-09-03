# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _inverse_state(self):
        res = super()._inverse_state()
        self._sync_stage_from_state()
        return res

    def _sync_stage_from_state(self):
        for task in self:
            if task.stage_id.task_state == task.state:
                continue
            stage = task._find_stage_for_state(task.state)
            if stage:
                task.stage_id = stage

    def _find_stage_for_state(self, state):
        self.ensure_one()
        if not state:
            return self.env["project.task.type"]
        return self.project_id.type_ids.filtered(
            lambda s: s.task_state == state and s.sync_state_to_stage
        )[:1]
