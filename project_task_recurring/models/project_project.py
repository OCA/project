# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProject(models.Model):

    _inherit = "project.project"

    task_schedule_ids = fields.One2many(
        comodel_name="project.task.schedule", inverse_name="project_id",
    )
