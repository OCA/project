# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProjectProject(models.Model):
    _inherit = "project.project"

    def _update_forecast_lines_trigger_fields(self):
        return ["stage_id"]

    def write(self, values):
        res = super().write(values)
        written_fields = list(values.keys())
        trigger_fields = self._update_forecast_lines_trigger_fields()
        if any(field in written_fields for field in trigger_fields):
            self.task_ids._update_forecast_lines()
        return res
