# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models

from ..utils import get_written_computed_fields


class ProjectProject(models.Model):
    _inherit = "project.project"

    def _update_forecast_lines_trigger_fields(self):
        return ["stage_id"]

    # TODO: Stored computed fields updates don't go through write,
    # but they do go through _write. Check if possible to override
    # that method instead, to avoid maintaing get_written_computed_fields
    def write(self, values):
        res = super().write(values)
        written_computed_fields = get_written_computed_fields(
            self, tuple(sorted(values))
        )
        trigger_fields = self._update_forecast_lines_trigger_fields()
        if any(field in written_computed_fields for field in trigger_fields):
            self.task_ids._update_forecast_lines()
        return res
