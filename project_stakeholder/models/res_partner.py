# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    stakeholder_ids = fields.One2many(
        "project.stakeholder",
        "partner_id",
        string="Stakeholder in Projects",
    )
