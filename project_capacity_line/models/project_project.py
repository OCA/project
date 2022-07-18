# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models

TRIGGER_FIELDS = {"stage_id"}


class ProjectProject(models.Model):
    _inherit = "project.project"

    def write(self, values):
        res = super().write(values)
        written_fields = set(values.keys())
        if written_fields & TRIGGER_FIELDS:
            self.task_ids._update_capacity_lines()
        return res
