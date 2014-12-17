# -*- coding: utf-8 -*-
from osv import orm
from openerp.tools.translate import _


class account_analytic(orm.Model):
    _inherit = 'account.analytic.account'

    def name_search(self, cr, uid, name, args=None,
                    operator='ilike', context=None, limit=80):
        if context is None:
            context = {}
        if not context.has_key('hours_block_search_invoice_id'):
            return super(project_project, self).name_search(self, cr, uid, name, args,
                    operator, context, )
        else:
            invoice_id = context['hours_block_search_invoice_id']
            invoice_line_obj = self.pool['account.invoice.line']
            invoice_lines_ids = invoice_line_obj.search(cr, uid,
                                                        [('invoice_id','=',invoice_id)], context=context)
            account = []
            for line in invoice_line_obj.browse(cr, uid, invoice_lines_ids, context=context):
                if line.account_analytic_id:
                    account.append(line.account_analytic_id.id)
            
            return self.name_get(cr, uid, account, context=context)
