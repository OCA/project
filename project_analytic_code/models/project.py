# Copyright 2021 Pierre Verkest
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    _rec_names_search = [
        "name",
        "analytic_account_code",
    ]

    analytic_account_code = fields.Char(
        string="Analytic code",
        related="analytic_account_id.code",
        store=True,
        index="btree_not_null",
    )

    @api.depends("analytic_account_code")
    def _compute_display_name(self):
        # res is null but avoid noqa: W8110
        res = super()._compute_display_name()
        for project in self:
            code = project.analytic_account_code
            if code:
                project.display_name = f"[{code}] {project.display_name}"
        return res
