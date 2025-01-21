# Copyright 2021-2025 - Pierre Verkest
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    project_ok = fields.Boolean(
        string="Available in projects",
        compute="_compute_project_ok",
        store=True,
        readonly=False,
        help="Check this box to be able to link this product with "
        "analytic line and project or task. Product cost will be used "
        "and displayed in project dashboard as consumable cost. "
        "So you'll be able to analyse consumable products cost per project.",
    )

    @api.depends("type")
    def _compute_project_ok(self):
        for record in self:
            if record.type == "consu":
                record.project_ok = True
            else:
                record.project_ok = False
