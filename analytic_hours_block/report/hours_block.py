# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import time
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class account_hours_block(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(account_hours_block, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time,
                                  'date_format': DEFAULT_SERVER_DATE_FORMAT,
                                  'analytic_lines': self._get_analytic_lines,
                                  })
        self.context = context

    def _get_analytic_lines(self, hours_block):
        al_pool = self.pool.get('account.analytic.line')
        aj_pool = self.pool.get('account.analytic.journal')
        tcj_ids = aj_pool.search(self.cr, self.uid,
                                 [('type', '=', 'general')])
        al_ids = al_pool.search(self.cr,
                                self.uid,
                                [('invoice_id', '=', hours_block.invoice_id.id),
                                 ('journal_id', 'in', tcj_ids),
                                 ],
                                order='date desc',
                                context=self.context)
        return al_pool.browse(self.cr, self.uid, al_ids, context=self.context)

report_sxw.report_sxw('report.account.hours.block',
                      'account.hours.block',
                      'addons/analytic_hours_block/report/hours_block.rml',
                      parser=account_hours_block)
