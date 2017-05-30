# -*- coding: utf-8 -*-
# Copyright (C) 2013,2017 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import fields, models


class AnalyticAccount(models.Model):
    """Add Contact to Analytic Accounts"""
    _inherit = 'account.analytic.account'
    location_id = fields.Many2one(
        'res.partner',
        'Service Location',
        domain="[('parent_id','child_of',partner_id)"
               ",('parent_id','!=',False)]",
        oldname='contact_id')
