# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import models, fields, api


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    _order = ('analytic_account_id, '
              'categ_sequence, '
              'sale_layout_cat_id, '
              'sequence, '
              'id')

    sequence = fields.Integer(
        string='Sequence',
        help="Gives the sequence order when displaying a list of lines.",
    )
    sale_layout_cat_id = fields.Many2one(
        comodel_name='sale_layout.category',
        string='Section',
    )
    categ_sequence = fields.Integer(
        related='sale_layout_cat_id.sequence',
        string='Layout Sequence', store=True,
        default=0,
    )


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_invoice_lines(self, contract, fiscal_position_id):
        _super = super(AccountAnalyticAccount, self)
        invoice_lines = _super._prepare_invoice_lines(contract,
                                                      fiscal_position_id)
        # with the defined _order, we know that the list of lines
        # returned by super is the same than the contract lines' order
        for idx, line in enumerate(contract.recurring_invoice_line_ids):
            invoice_lines[idx][2].update({
                'sequence': line.sequence,
                'sale_layout_cat_id': line.sale_layout_cat_id.id,
                'categ_sequence': line.categ_sequence,
            })
        return invoice_lines
