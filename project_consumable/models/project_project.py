# Copyright 2021-2025 Pierre Verkest
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    timesheet_ids = fields.One2many(
        domain=[("product_id", "=", None)],
    )

    consumable_count = fields.Integer(
        compute="_compute_consumable_count",
        help="Number of consumable lines collected.",
    )

    def _compute_consumable_count(self):
        read_group = {
            group["project_id"][0]: group["project_id_count"]
            for group in self.env["account.analytic.line"].read_group(
                [
                    ("project_id", "in", self.ids),
                    ("product_id", "!=", False),
                ],
                ["project_id"],
                ["project_id"],
            )
        }
        for project in self:
            project.consumable_count = read_group.get(project.id, 0)
