# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    account_hours_block_ids = fields.One2many(
        string="Hours Block",
        comodel_name="account.hours.block",
        inverse_name="invoice_id",
    )
