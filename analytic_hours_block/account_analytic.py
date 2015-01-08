# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Vincent Renaville, ported by Joel Grand-Guillaume
#    Copyright 2010-2012 Camptocamp SA
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
##############################################################################
from openerp.osv import orm


class account_analytic(orm.Model):
    _inherit = 'account.analytic.account'

    def name_search(self, cr, uid, name, args=None,
                    operator='ilike', context=None, limit=80):
        if context is None:
            context = {}
        if 'hours_block_search_invoice_id' in context:
            invoice_id = context['hours_block_search_invoice_id']
            invoice_line_obj = self.pool['account.invoice.line']
            invoice_lines_ids = invoice_line_obj.search(
                cr, uid, [('invoice_id', '=', invoice_id)], context=context)
            account = []
            for line in invoice_line_obj.browse(cr, uid,
                                                invoice_lines_ids,
                                                context=context):
                if line.account_analytic_id:
                    account.append(line.account_analytic_id.id)

            return self.name_get(cr, uid, account, context=context)
        else:
            return super(account_analytic, self).name_search(
                cr=cr, uid=uid, name=name, args=args, operator=operator,
                context=context, limit=limit)
