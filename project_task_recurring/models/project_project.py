# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProject(models.Model):

    _inherit = "project.project"

    task_schedule_ids = fields.One2many(
        comodel_name="project.task.schedule", inverse_name="project_id",
    )

    def action_schedule_tasks(self):
        self.schedule_task_ids._create_tasks()
