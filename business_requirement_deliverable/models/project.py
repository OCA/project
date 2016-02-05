# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class Project(models.Model):
    _inherit = "project.project"

    pricelist_id = fields.Many2one(
        string='Pricelist',
        comodel_name='product.pricelist',
        domain=[('type', '=', 'sale')],
        help='Pricelist for sales estimation'
    )
