# Copyright 2014 Daniel Reis
# Copyright 2024 Tecnativa - Víctor Matínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models

from odoo.addons.project.models.project_task import CLOSED_STATES


class ProjectTaskType(models.Model):
    """Added state in the Project Task Type."""

    _inherit = "project.task.type"

    def _get_task_states(self):
        return self.env["project.task"].fields_get(allfields=["state"])["state"][
            "selection"
        ]

    task_state = fields.Selection(selection="_get_task_states")

    def write(self, vals):
        res = super().write(vals)
        if vals.get("task_state"):
            self._apply_task_state()
        return res

    def _apply_task_state(self):
        stages = self.filtered(lambda s: s.task_state in CLOSED_STATES)
        self.env["project.task"].search(
            [
                ("stage_id", "in", stages.ids),
                ("state", "not in", list(CLOSED_STATES)),
            ]
        )._inverse_stage_id()
