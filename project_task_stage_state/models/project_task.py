# Copyright 2014 Daniel Reis
# Copyright 2024 Tecnativa - Víctor Matínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _set_task_state(self):
        for task in self:
            if task.stage_id.task_state and task.stage_id.task_state != task.state:
                task.state = task.stage_id.task_state

    def write(self, vals):
        res = super().write(vals)
        if "stage_id" in vals:
            self._set_task_state()
        return res
