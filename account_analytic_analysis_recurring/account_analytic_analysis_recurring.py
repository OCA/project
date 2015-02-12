# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from dateutil.relativedelta import relativedelta
import datetime
import logging
import time

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.decimal_precision import decimal_precision as dp

_logger = logging.getLogger(__name__)


class AccountAnalyticInvoiceLine(orm.Model):
    _name = "account.analytic.invoice.line"

    def _amount_line(
            self, cr, uid, ids, prop, unknow_none, unknow_dict, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.quantity * line.price_unit
            if line.analytic_account_id.pricelist_id:
                cur = line.analytic_account_id.pricelist_id.currency_id
                res[line.id] = self.pool.get('res.currency').round(
                    cr, uid, cur, res[line.id])
        return res

    _columns = {
        'product_id': fields.many2one(
            'product.product', 'Product', required=True),
        'analytic_account_id': fields.many2one(
            'account.analytic.account', 'Analytic Account'),
        'name': fields.text('Description', required=True),
        'quantity': fields.float('Quantity', required=True),
        'uom_id': fields.many2one(
            'product.uom', 'Unit of Measure', required=True),
        'price_unit': fields.float('Unit Price', required=True),
        'price_subtotal': fields.function(
            _amount_line, string='Sub Total',
            type="float", digits_compute=dp.get_precision('Account')),
    }
    _defaults = {
        'quantity': 1,
    }

    def product_id_change(
            self, cr, uid, ids, product, uom_id, qty=0, name='',
            partner_id=False, price_unit=False, pricelist_id=False,
            company_id=None, context=None):
        context = context or {}
        uom_obj = self.pool.get('product.uom')
        company_id = company_id or False
        context.update(
            {'company_id': company_id,
             'force_company': company_id,
             'pricelist_id': pricelist_id})

        if not product:
            return {
                'value': {'price_unit': 0.0},
                'domain': {'product_uom': []}}
        if partner_id:
            part = self.pool.get('res.partner').browse(
                cr, uid, partner_id, context=context)
            if part.lang:
                context.update({'lang': part.lang})

        result = {}
        res = self.pool.get('product.product').browse(
            cr, uid, product, context=context)
        result.update(
            {'name': res.partner_ref or False,
             'uom_id': uom_id or res.uom_id.id or False,
             'price_unit': res.list_price or 0.0})
        if res.description:
            result['name'] += '\n' + res.description

        res_final = {'value': result}
        if result['uom_id'] != res.uom_id.id:
            new_price = uom_obj._compute_price(
                cr, uid, res.uom_id.id,
                res_final['value']['price_unit'], result['uom_id'])
            res_final['value']['price_unit'] = new_price
        return res_final


class AccountAnalyticAccount(orm.Model):
    _name = "account.analytic.account"
    _inherit = "account.analytic.account"

    _columns = {
        'recurring_invoice_line_ids': fields.one2many(
            'account.analytic.invoice.line', 'analytic_account_id',
            'Invoice Lines'),
        'recurring_invoices': fields.boolean(
            'Generate recurring invoices automatically'),
        'recurring_rule_type': fields.selection(
            [('daily', 'Day(s)'),
             ('weekly', 'Week(s)'),
             ('monthly', 'Month(s)'),
             ('yearly', 'Year(s)'),
             ], 'Recurrency',
            help="Invoice automatically repeat at specified interval"),
        'recurring_interval': fields.integer(
            'Repeat Every', help="Repeat every (Days/Week/Month/Year)"),
        'recurring_next_date': fields.date('Date of Next Invoice'),
    }

    _defaults = {
        'recurring_interval': 1,
        'recurring_next_date': lambda *a: time.strftime('%Y-%m-%d'),
        'recurring_rule_type': 'monthly'
    }

    def copy(self, cr, uid, id, default=None, context=None):
        # Reset next invoice date
        default['recurring_next_date'] = \
            self._defaults['recurring_next_date']()
        return super(AccountAnalyticAccount, self).copy(
            cr, uid, id, default=default, context=context)

    def onchange_recurring_invoices(
            self, cr, uid, ids, recurring_invoices,
            date_start=False, context=None):
        value = {}
        if date_start and recurring_invoices:
            value = {'value': {'recurring_next_date': date_start}}
        return value

    def _prepare_invoice_line(self, cr, uid, line, invoice_id, context=None):
        fpos_obj = self.pool['account.fiscal.position']
        lang_obj = self.pool['res.lang']
        product = line.product_id
        account_id = product.property_account_income.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ.id
        contract = line.analytic_account_id
        fpos = contract.partner_id.property_account_position or False
        account_id = fpos_obj.map_account(cr, uid, fpos, account_id)
        taxes = product.taxes_id or False
        tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
        if 'old_date' in context:
            lang_ids = lang_obj.search(
                cr, uid, [('code', '=', contract.partner_id.lang)],
                context=context)
            format = lang_obj.browse(
                cr, uid, lang_ids, context=context)[0].date_format
            line.name = line.name.replace(
                '#START#', context['old_date'].strftime(format))
            line.name = line.name.replace(
                '#END#', context['next_date'].strftime(format))
        return {
            'name': line.name,
            'account_id': account_id,
            'account_analytic_id': contract.id,
            'price_unit': line.price_unit or 0.0,
            'quantity': line.quantity,
            'uos_id': line.uom_id.id or False,
            'product_id': line.product_id.id or False,
            'invoice_id': invoice_id,
            'invoice_line_tax_id': [(6, 0, tax_id)],
        }

    def _prepare_invoice(self, cr, uid, contract, context=None):
        if context is None:
            context = {}
        inv_obj = self.pool['account.invoice']
        journal_obj = self.pool['account.journal']
        if not contract.partner_id:
            raise orm.except_orm(
                _('No Customer Defined!'),
                _("You must first select a Customer for Contract %s!") %
                contract.name)
        partner = contract.partner_id
        fpos = partner.property_account_position or False
        journal_ids = journal_obj.search(
            cr, uid,
            [('type', '=', 'sale'),
             ('company_id', '=', contract.company_id.id or False)],
            limit=1)
        if not journal_ids:
            raise orm.except_orm(
                _('Error!'),
                _('Please define a sale journal for the company "%s".') %
                (contract.company_id.name or '',))
        partner_payment_term = partner.property_payment_term.id
        inv_data = {
            'reference': contract.code or False,
            'account_id': partner.property_account_receivable.id,
            'type': 'out_invoice',
            'partner_id': partner.id,
            'currency_id': partner.property_product_pricelist.currency_id.id,
            'journal_id': len(journal_ids) and journal_ids[0] or False,
            'date_invoice': contract.recurring_next_date,
            'origin': contract.name,
            'fiscal_position': fpos and fpos.id,
            'payment_term': partner_payment_term,
            'company_id': contract.company_id.id or False,
        }
        invoice_id = inv_obj.create(cr, uid, inv_data, context=context)
        for line in contract.recurring_invoice_line_ids:
            invoice_line_vals = self._prepare_invoice_line(
                cr, uid, line, invoice_id, context=context)
            self.pool['account.invoice.line'].create(
                cr, uid, invoice_line_vals, context=context)
        inv_obj.button_compute(cr, uid, [invoice_id], context=context)
        return invoice_id

    def recurring_create_invoice(self, cr, uid, automatic=False, context=None):
        if context is None:
            context = {}
        current_date = time.strftime('%Y-%m-%d')
        contract_ids = self.search(
            cr, uid,
            [('recurring_next_date', '<=', current_date),
             ('state', '=', 'open'),
             ('recurring_invoices', '=', True)])
        for contract in self.browse(cr, uid, contract_ids, context=context):
            next_date = datetime.datetime.strptime(
                contract.recurring_next_date or current_date, "%Y-%m-%d")
            interval = contract.recurring_interval
            old_date = next_date
            if contract.recurring_rule_type == 'daily':
                new_date = next_date + relativedelta(days=+interval)
            elif contract.recurring_rule_type == 'weekly':
                new_date = next_date + relativedelta(weeks=+interval)
            else:
                new_date = next_date + relativedelta(months=+interval)
            context['old_date'] = old_date
            context['next_date'] = new_date
            # Force company for correct evaluate domain access rules
            context['force_company'] = contract.company_id.id
            # Re-read contract with correct company
            contract = self.browse(cr, uid, contract.id, context=context)
            self._prepare_invoice(
                cr, uid, contract, context=context
            )
            self.write(
                cr, uid, [contract.id],
                {'recurring_next_date': new_date.strftime('%Y-%m-%d')},
                context=context
            )
        return True
