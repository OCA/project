# Copyright 2026 Forgeflow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    task_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Task Sequence",
        ondelete="set null",
        copy=False,
        help="Sequence used for task codes in this project. "
        "If not set, the global task sequence is used.",
    )
