# Copyright 2026 - Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    is_qa_stage = fields.Boolean(
        string="QA Stage",
        help="Mark this stage as an internal testing / QA stage. A task's QA "
        "checklist is generated when it enters a stage flagged here, and a "
        "warning is raised if it leaves such a stage with an incomplete "
        "checklist.",
    )
