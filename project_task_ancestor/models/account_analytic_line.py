# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    ancestor_task_id = fields.Many2one(
        comodel_name="project.task",
        related="task_id.ancestor_id",
        store=True,
        index="btree_not_null",
    )
