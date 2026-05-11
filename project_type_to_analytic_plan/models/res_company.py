# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    project_types_root_analytic_plan_id = fields.Many2one(
        comodel_name="account.analytic.plan",
        string="Root Analytic Plan for Project Types",
        help="Root analytic plan used for synchronizing project types",
    )
