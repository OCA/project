# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    ancestor_id = fields.Many2one(
        comodel_name="project.task",
        string="Ancestor Task",
        compute="_compute_ancestor_id",
        index="btree_not_null",
        recursive=True,
        store=True,
    )

    @api.depends("parent_id.ancestor_id")
    def _compute_ancestor_id(self):
        for task in self:
            task.ancestor_id = task.parent_id.ancestor_id or task.parent_id
