# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp.osv import orm, fields
from odoo import _, api, fields, models


class Product(models.Model):
    _inherit = 'product.product'

    is_in_hours_block = fields.Boolean(
        string="Accounted for hours block?",
        help="Specify if you want to have invoice lines "
             "containing this product to be considered for hours blocks.",
    )
