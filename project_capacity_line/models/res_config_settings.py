# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    capacity_line_granularity = fields.Selection(
        related="company_id.capacity_line_granularity", readonly=False
    )
    capacity_line_horizon = fields.Integer(
        related="company_id.capacity_line_horizon", readonly=False
    )

    group_capacity_line_on_quotation = fields.Boolean(
        "Capacity Line on Quotations",
        implied_group="project_capacity_line.group_capacity_line_on_quotation",
    )
