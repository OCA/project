# Copyright 2026 Ledo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectType(models.Model):
    _inherit = "project.type"

    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Project Sequence",
        copy=False,
        help=(
            "Projects of this type take their sequence code from this sequence. "
            "When left empty, the default project sequence is used."
        ),
    )
