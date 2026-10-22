# Copyright 2026 glueckkanja AG
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    reuse_project_id = fields.Many2one(
        "project.project",
        domain=[("allow_billable", "=", True), ("is_template", "=", False)],
        copy=False,
        help="Project reused as the project of new sales orders of this customer. "
        "If left empty, it is filled with the project of the first confirmed "
        "sales order containing a product flagged 'Reuse Project'.",
    )
