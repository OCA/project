# Copyright Binhex 2024
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"
    project_status = fields.Many2one(
        "project.project.stage",
        string="Project Status",
        copy=False,
        ondelete="restrict",
        index=True,
        store=True,
        related="project_id.stage_id",
    )
