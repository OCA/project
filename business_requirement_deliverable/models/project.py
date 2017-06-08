# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class Project(models.Model):
    _inherit = "project.project"

    pricelist_id = fields.Many2one(
        string='Estimation Pricelist',
        comodel_name='product.pricelist',
        domain=[('type', '=', 'sale')],
        help='''Pricelist used for the estimation of the Business Requirements
        Deliverables linked to this project.
        Currency of the Deliverables will be the one from this pricelist.'''
    )
