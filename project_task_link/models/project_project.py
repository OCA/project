# Copyright 2023 Quartile Limited

from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    label_tasks_custom = fields.Char(compute="_compute_label_tasks_custom")

    def _compute_label_tasks_custom(self):
        for record in self:
            record.label_tasks_custom = record.label_tasks
