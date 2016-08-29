# -*- coding: utf-8 -*-
#
#    Author: Yannick Vaucher, ported by Denis Leemann
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
import time

from openerp import SUPERUSER_ID
from openerp.osv import osv, orm, fields
from openerp.tools.translate import _
import cProfile


STATES = [
    ('draft', "Draft"),
    ('confirm', "Confirmed"),
]


class AccountAnalyticLine(orm.Model):
    # ./parts/server/addons/analytic/analytic.py
    _inherit = 'account.analytic.line'

    # OK
    def _get_default_invoiced_product(self, cr, uid, context=None):
        if context is None:
            context = {}
        hr_timesheet_obj = self.pool['hr.analytic.timesheet']

        return hr_timesheet_obj._getEmployeeProduct(
            cr=cr, uid=uid, context=context)

    _columns = {
        # TODO bloquer l'édition d'une ligne si le tatus est confirmé
        'state': fields.selection(STATES, 'States', required=True),
        'invoiced_hours': fields.float(
            help="Amount of hours that you want to charge your customer for "
            "(e.g. hours spent 2:12, invoiced 2:15). You can use the 'Create "
            "invoice' wizard from timesheet line for that purpose",
        ),
        'invoiced_product_id': fields.many2one(
            'product.product', 'Product',
            help="Product used to generate the invoice in case it differs "
            "from the product used to compute the costs.",
        ),
    }

    _defaults = {
        'state': 'draft',
        'invoiced_product_id': _get_default_invoiced_product,
    }

    def _set_remaining_hours_create(self, cr, uid, vals, context=None):
        """OVERWRITE calculation is now made with invoiced_hours
        """
        if not vals.get('task_id'):
            return
        hours = vals.get('invoiced_hours', 0.0)
        # We can not do a write else we will have a recursion error
        cr.execute(
            'UPDATE project_task '
            'SET remaining_hours=remaining_hours - %s '
            'WHERE id=%s', (hours, vals['task_id']))
        self._trigger_projects(cr, uid, [vals['task_id']], context=context)
        return vals

    def _set_remaining_hours_write(self, cr, uid, ids, vals, context=None):
        """ OVERWRITE calculation is made with: invoiced_hours in place of:
            unit_amount
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        for line in self.browse(cr, uid, ids):
            # in OpenERP if we set a value to nil vals become False
            old_task_id = line.task_id and line.task_id.id or None
            # if no task_id in vals we assume it is equal to old
            new_task_id = vals.get('task_id', old_task_id)
            # we look if value has changed
            if (new_task_id != old_task_id) and old_task_id:
                self._set_remaining_hours_unlink(cr, uid, [line.id], context)
                if new_task_id:
                    data = {'task_id': new_task_id,
                            'to_invoice': vals.get('to_invoice',
                                                   line.to_invoice.id),
                            'unit_amount': vals.get('unit_amount',
                                                    line.unit_amount),
                            'invoiced_hours': vals.get('invoiced_hours',
                                                       line.invoiced_hours)
                            }
                    self._set_remaining_hours_create(cr, uid, data, context)
                    self._trigger_projects(
                        cr, uid, list(set([old_task_id, new_task_id])),
                        context=context)
                return ids
            if new_task_id:
                hours = vals.get('invoiced_hours', line.invoiced_hours)
                old_hours = line.invoiced_hours if old_task_id else 0.0
                # We can not do a write else we will have a recursion error
                cr.execute(
                    'UPDATE project_task '
                    'SET remaining_hours=remaining_hours - %s + (%s) '
                    'WHERE id=%s', (hours, old_hours, new_task_id))
                self._trigger_projects(cr, uid, [new_task_id], context=context)
        return ids

    def _set_remaining_hours_unlink(self, cr, uid, ids, context=None):
        """ OVERWRITE changed the calculation method of remaining_hours with
            invoiced_hours in place of unit_amount
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        for line in self.browse(cr, uid, ids):
            if not line.task_id:
                continue
            hours = line.invoiced_hours or 0.0
            cr.execute(
                'UPDATE project_task '
                'SET remaining_hours=remaining_hours + %s '
                'WHERE id=%s', (hours, line.task_id.id))
        return ids

    def _check(self, cr, uid, ids, context=None):
        """ OVERWRITE _check to check state of the line instead of the sheet
        """
        for line in self.browse(self, cr, uid, ids, context=context):
            if line.state == 'confirm':
                if (uid != line.account_id.user_id.id and
                        uid != SUPERUSER_ID):
                    raise orm.except_orm(
                        _(u"Only the project manager can modify an entry in a "
                          "confirmed timesheet line. Please contact him to set"
                          " this entry to draft in order to edit it."))
        return True

    def create(self, cr, uid, vals, context=None):
        if 'invoiced_hours' in vals:
            if not vals['invoiced_hours']:
                vals['invoiced_hours'] = vals['unit_amount']
        res = super(AccountAnalyticLine, self).create(
            cr, uid, vals, context=context)

        return res

    def write(self, cr, uid, ids, vals, context=None):
        """ Only project manager and superusers can change states """
        if vals:
            if 'state' in vals:
                errors = []
                lines = self.browse(cr, uid, ids, context=context)
                user = self.pool['res.users']
                grp = user.has_group(cr, uid, 'project.group_project_manager')
                for line in lines:
                    if (uid != line.account_id.user_id.id and
                            uid != SUPERUSER_ID and not grp):
                        errors.append(line)

                if errors:
                    raise orm.except_orm(
                        _(u'Error'),
                        _(u"You dont have the rights to modify the following "
                            "entries %s") % (
                            errors)
                    )
        return super(AccountAnalyticLine, self).write(
            cr, uid, ids, vals, context=context)

    # TODO verifier la fonction pour le test avec self
    # sur l'assiniation de product.
    # vérifier l' assignation sur les self du retour
    # TODO: pas utilisée pour le moment
    def _get_invoice_grouping_key(self, cr, uid, ids, context=None):
        """ Get key for grouping in invoicing """

        product = (self.invoiced_product or
                   self.product_id)
        return (product_id,
                self.product_uom_id.id,
                self.user_id.id,
                self.to_invoice.id,
                self.account_id,
                self.journal_id.type)

    def action_confirm(self, cr, uid, ids, context=None):
        user = self.pool['res.users']
        if(user.has_group(cr, uid, 'project.group_project_manager')):
            return self.write(cr, uid, ids, vals={
                'state': 'confirm'}, context=context)

    def action_reset_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, vals={
            'state': 'draft'}, context=context)

    # TODO Renommer l'appel à mettre dans la vue
    # TODO page avec le onchange
    def onchange_to_invoice_set_invoiced_hours(self, cr, id,
                                               onchangeInvoice, context=None):
        """ Change invoiced_hours according to invoicing rate factor """
        if self.to_invoice:
            discount = self.unit_amount * (self.to_invoice.factor / 100.0)
            self.invoiced_hours = self.unit_amount - discount

    def invoice_cost_create(self, cr, uid, ids, data=None, context=None):
        analytic_account_obj = self.pool['account.analytic.account']
        account_payment_term_obj = self.pool['account.payment.term']
        invoice_obj = self.pool['account.invoice']
        product_obj = self.pool['product.product']
        invoice_factor_obj = self.pool['hr_timesheet_invoice.factor']
        fiscal_pos_obj = self.pool['account.fiscal.position']
        product_uom_obj = self.pool['product.uom']
        invoice_line_obj = self.pool['account.invoice.line']
        res_partner_obj = self.pool['res.partner']
        aal_obj = self.pool['account.analytic.line']
        invoices = []
        if context is None:
            context = {}
        if data is None:
            data = {}

        journal_types = {}

        # prepare for iteration on journal and accounts
        for line in aal_obj.browse(cr, uid, ids, context=context):
            if line.journal_id.type not in journal_types:
                journal_types[line.journal_id.type] = set()
            journal_types[line.journal_id.type].add(line.account_id.id)
        for journal_type, account_ids in journal_types.items():
            for account in analytic_account_obj.browse(
                    cr, uid, list(account_ids), context=context):
                partner = account.partner_id

                if (not partner) or not (account.pricelist_id):
                    raise osv.except_osv(_('Analytic Account Incomplete!'),
                                         _('Contract incomplete. Please fill \
                                            in the Customer and Pricelist \
                                            fields.'))
                context2 = context.copy()
                context2['lang'] = account.partner_id.lang
                # set company_id in context, so the correct default journal
                # will be selected when creating the invoice
                context2['company_id'] = account.company_id.id
                # set force_company in context so the correct properties are
                # selected (eg. income account, receivable account)
                context2['force_company'] = account.company_id.id

                partner = res_partner_obj.browse(
                    cr, uid, account.partner_id.id, context=context2)

                date_due = False
                if partner.property_payment_term:
                    pterm_list = account_payment_term_obj.compute(cr, uid,
                                                                  partner.property_payment_term.id, value=1,
                                                                  date_ref=time.strftime('%Y-%m-%d'))
                    if pterm_list:
                        pterm_list = [line[0] for line in pterm_list]
                        pterm_list.sort()
                        date_due = pterm_list[-1]

                curr_invoice = {
                    'name': time.strftime('%d/%m/%Y') + ' - ' + account.name,
                    'partner_id': account.partner_id.id,
                    'company_id': account.company_id.id,
                    'payment_term': partner.property_payment_term.id or False,
                    'account_id': partner.property_account_receivable.id,
                    'currency_id': account.pricelist_id.currency_id.id,
                    'date_due': date_due,
                    'fiscal_position': account.partner_id.property_account_position.id
                }

                last_invoice = invoice_obj.create(
                    cr, uid, curr_invoice, context=context2)
                invoices.append(last_invoice)

                # TODO partie à modifier
                # Les aal sont normalement groupées par produit => le but est de les grouper
                # but modifier le groupement
                """ Modification of:
                unit_amount     =>  invoiced_hours
                product_id      =>  invoiced_product_id
                """
                cr.execute("""SELECT invoiced_product_id, user_id, to_invoice,
                    sum(amount), sum(invoiced_hours), product_uom_id
                        FROM account_analytic_line as line
                        LEFT JOIN account_analytic_journal journal
                        ON (line.journal_id = journal.id)
                        WHERE account_id = %s
                        AND line.id IN %s
                        AND journal.type = %s
                        AND to_invoice IS NOT NULL
                        GROUP BY invoiced_product_id, user_id, to_invoice, product_uom_id""", (account.id, tuple(ids), journal_type))

                for invoiced_product_id, user_id, factor_id, total_price, qty, uom in cr.fetchall():
                    context2.update({'uom': uom})
# produit peut-être à modfier
                    if data.get('product'):
                        # force product, use its public price
                        invoiced_product_id = data['product'][0]
                        unit_price = self._get_invoice_price(
                            cr, uid, account, invoiced_product_id, user_id, qty, context2)
                    elif journal_type == 'general' and invoiced_product_id:
                        # timesheets, use sale price
                        unit_price = self._get_invoice_price(
                            cr, uid, account, invoiced_product_id, user_id, qty, context2)
                    else:
                        # expenses, using price from amount field
                        unit_price = total_price * -1.0 / qty
# fin produit peut-être à modifier
                    factor = invoice_factor_obj.browse(
                        cr, uid, factor_id, context=context2)
                    # factor_name = factor.customer_name and line_name + ' - ' + factor.customer_name or line_name
                    factor_name = factor.customer_name
                    curr_line = {
                        'price_unit': unit_price,
                        'quantity': qty,
                        'invoiced_product_id': invoiced_product_id or False,
                        'discount': factor.factor,
                        'invoice_id': last_invoice,
                        'name': factor_name,
                        'uos_id': uom,
                        'account_analytic_id': account.id,
                    }
                    product = product_obj.browse(
                        cr, uid, invoiced_product_id, context=context2)
                    if product:
                        factor_name = product_obj.name_get(
                            cr, uid, [invoiced_product_id], context=context2)[0][1]
                        if factor.customer_name:
                            factor_name += ' - ' + factor.customer_name

                        general_account = product.property_account_income or product.categ_id.property_account_income_categ
                        if not general_account:
                            raise osv.except_osv(
                                _("Configuration Error!"),
                                _("Please define income account for product \
                                    '%s'.") % product.name)
                        taxes = product.taxes_id or general_account.tax_ids
                        tax = fiscal_pos_obj.map_tax(
                            cr,
                            uid,
                            account.partner_id.property_account_position,
                            taxes)
                        curr_line.update({
                            'invoice_line_tax_id': [(6, 0, tax)],
                            'name': factor_name,
                            'invoice_line_tax_id': [(6, 0, tax)],
                            'account_id': general_account.id,
                        })
                    #
                    # Compute for lines
                    #
                    """invoiced_product_id in place of product_id
                    """
                    cr.execute("SELECT * FROM account_analytic_line \
                        WHERE account_id = %s and id IN %s \
                        AND invoiced_product_id=%s and to_invoice=%s \
                        ORDER BY account_analytic_line.date",
                               (account.id,
                                tuple(ids),
                                invoiced_product_id,
                                factor_id))

                    line_ids = cr.dictfetchall()
                    note = []
                    for line in line_ids:
                        # set invoice_line_note
                        details = []
                        if data.get('date', False):
                            details.append(line['date'])
                        if data.get('time', False):
                            if line['product_uom_id']:
                                """ invoiced_hours instead of unit_price """
                                details.append("%s %s" % (line['invoiced_hours'], product_uom_obj.browse(
                                    cr,
                                    uid,
                                    [line['product_uom_id']],
                                    context2)[0].name))
                            else:
                                """ invoiced_hours instead of unit_price """
                                details.append("%s" %
                                               (line['invoiced_hours'], ))
                        if data.get('name', False):
                            details.append(line['name'])
                        note.append(
                            u' - '.join(map(lambda x: unicode(x) or '', details)))
                    if note:
                        curr_line['name'] += "\n" + \
                            ("\n".join(map(lambda x: unicode(x) or '', note)))
                    invoice_line_obj.create(
                        cr, uid, curr_line, context=context)
                    cr.execute("update account_analytic_line set \
                        invoice_id=%s WHERE account_id = %s and id IN %s", (
                        last_invoice, account.id, tuple(ids)))
                invoice_obj.button_reset_taxes(
                    cr, uid, [last_invoice], context)
        return invoices

    def check_invoiceable_line(self, cr, uid, ids, context=None):
        # check that no analytic line is in a not-done timesheet
        cr.execute("""
            SELECT al.id
            FROM account_analytic_line al
            WHERE state = 'draft'
        """)
        open_timesheet_ids = set([x[0] for x in cr.fetchall()])
        # Intersect set(ids) and set(open_timesheet_ids)
        # to see if any ID is common to both sets
        intersect = set(ids) & open_timesheet_ids
        if len(intersect) > 0:
            msg = ''
            for line in self.browse(cr, uid, list(intersect), context=context):
                msg += _('Name: ') + line.name
                msg += _(", User: ") + line.user_id.name
                msg += "\n"
            raise osv.except_osv(
                _('Some of the analytic lines are '
                  'in not-approved timesheets!'),
                msg)
    # TODO faire un override to add unit_price computation adn quantity based
    # on invoiced_hours
    # def _prepare_cost_invoice_line(self, invoice_id, product_id,
    #                                uom, user_id,
    #                                factor_id, account, analytic_lines,
    #                                journal_type, data):

    def check_confirmation(self, cr, uid, ids, context=None):
        cr.execute("""
            SELECT al.id
            FROM account_analytic_line al
            WHERE state ='draft'
            """)
        confirmed_aal_ids = set([x[0] for x in cr.fetchall()])
        intersect = set(ids) & confirmed_aal_ids
        if len(intersect) > 0:
            raise osv.except_osv(
                _('Some of the analytic lines are in draft state')
            )
