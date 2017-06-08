# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api, _
from openerp.exceptions import except_orm


class HrAnalyticTimesheet(models.Model):
    _inherit = "hr.analytic.timesheet"

    @api.multi
    def _get_sale_lines(self):
        task_works = self.env['project.task.work'].search(
            [('hr_analytic_timesheet_id', '=', self.id)])
        return task_works.mapped('task_id.sale_line_id')


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def _get_sale_lines(self):
        timesheet_obj = self.env['hr.analytic.timesheet']
        timesheet = timesheet_obj.search([('line_id', 'in', self.ids)])
        task_works = self.env['project.task.work'].search(
            [('hr_analytic_timesheet_id', 'in', timesheet.ids)])
        return task_works.mapped('task_id.sale_line_id')

    @api.multi
    def invoice_cost_create(self, data=None):
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        analytic_line_obj = self.env['account.analytic.line']
        invoices = self.env['account.invoice']
        if data is None:
            data = {}

        # use key (partner/account, company, currency)
        # creates one invoice per key
        invoice_grouping = {}

        # prepare for iteration on journal and accounts
        for line in self:
            key = (line.account_id.id,
                   line.account_id.company_id.id,
                   line.account_id.pricelist_id.currency_id.id)
            invoice_grouping.setdefault(key, analytic_line_obj)
            invoice_grouping[key] = invoice_grouping[key] | line

        for (key_id, company_id, currency_id), analytic_lines in \
                invoice_grouping.items():
            # key_id is an account.analytic.account
            account = analytic_lines[0].account_id
            partner = account.partner_id  # will be the same for every line
            if (not partner) or not (currency_id):
                raise except_orm(_('Error!'), _(
                    'Contract incomplete. Please fill in the Customer and '
                    'Pricelist fields for %s.') % (account.name))

            curr_invoice = self._prepare_cost_invoice(
                partner, company_id, currency_id, analytic_lines)
            invoice_context = dict(
                self._context, lang=partner.lang, force_company=company_id,
                company_id=company_id)
            last_invoice = invoice_obj.with_context(invoice_context).create(
                curr_invoice)
            invoices = invoices | last_invoice
            # use key (product, uom, user, invoiceable,
            # analytic account, journal type)
            # creates one invoice line per key
            invoice_lines_grouping = {}
            for analytic_line in analytic_lines:
                if not analytic_line.to_invoice:
                    raise except_orm(_('Error!'), _(
                        'Trying to invoice non invoiceable line for %s.') % (
                        analytic_line.product_id.name))
                key = (analytic_line.product_id.id,
                       analytic_line.product_uom_id.id,
                       analytic_line.user_id.id,
                       analytic_line.to_invoice.id,
                       analytic_line.account_id,
                       analytic_line.journal_id.type)
                analytic_line = analytic_line_obj.with_context(
                    invoice_context).browse(
                    [line.id for line in analytic_line])
                invoice_lines_grouping.setdefault(key, []).append(
                    analytic_line)

            # finally creates the invoice line
            for (product_id, uom, user_id, factor_id, account, journal_type),\
                    lines_to_invoice in invoice_lines_grouping.items():
                curr_invoice_line = self.with_context(
                    invoice_context)._prepare_cost_invoice_line(
                    last_invoice.id, product_id, uom, user_id, factor_id,
                    account, lines_to_invoice, journal_type, data)
                new_invoice_line = invoice_line_obj.create(curr_invoice_line)
                sale_lines = analytic_lines._get_sale_lines()
                sale_lines.write(
                    {'invoice_lines': [(6, 0, [new_invoice_line.id])]})
                sale_lines.mapped('order_id').write(
                    {'invoice_ids': [(4, last_invoice.id)],
                     'state': 'done'})

            analytic_lines.write({'invoice_id': last_invoice.id})
            invoices.button_reset_taxes()
        return invoices.ids
