# Copyright 2026 - Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class ProjectTaskQaChecklistTemplate(models.Model):
    _name = "project.task.qa.checklist.template"
    _description = "QA Checklist Criterion Template"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, translate=True)
    always_applicable = fields.Boolean(
        default=False,
        help="If set, this criterion applies to every task entering a QA "
        "stage, regardless of its tags.",
    )
    tag_ids = fields.Many2many(
        comodel_name="project.tags",
        string="Tags",
        help="If any of these tags is on the task, this criterion is "
        "generated. Ignored when 'Always Applicable' is set.",
    )
    help_text = fields.Text(help="Optional guidance shown to the tester.")
    active = fields.Boolean(default=True)
