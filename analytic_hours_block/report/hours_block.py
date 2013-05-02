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

import time
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class account_hours_block(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(account_hours_block, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'date_format': DEFAULT_SERVER_DATE_FORMAT,
            'analytic_lines': self._get_analytic_lines,
        })
        self.context = context

    def _get_analytic_lines(self, hours_block):
        al_pool = self.pool.get('account.analytic.line')
        aj_pool = self.pool.get('account.analytic.journal')
        tcj_ids = aj_pool.search(self.cr,self.uid,[('type','=','general')])
        al_ids = al_pool.search(
                self.cr,
                self.uid,
                [('invoice_id', '=', hours_block.invoice_id.id),('journal_id','in',tcj_ids)],
                order='date desc',
                context=self.context)
        return al_pool.browse(self.cr, self.uid, al_ids, context=self.context)

report_sxw.report_sxw('report.account.hours.block', 'account.hours.block', 'addons/analytic_hours_block/report/hours_block.rml', parser=account_hours_block)
