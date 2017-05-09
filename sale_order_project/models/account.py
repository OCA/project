# -*- coding: utf-8 -*-
# © 2016 Didotech srl (http://www.didotech.com)
# © Andrei Levin <andrei.levin@didotech.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    sale_order_ids = fields.One2many(
        'sale.order',
        'project_id',
        string='Sale Orders'
    )
