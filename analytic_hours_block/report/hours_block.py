##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from mx.DateTime import *
from report import report_sxw

#import xml.dom.minidom
#import re


class account_hours_block(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(account_hours_block, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'format_date': self._get_and_change_date_format_for_swiss,
            'analytic_lines': self._get_analytic_lines,
        })
        self.context = context

    def _get_analytic_lines(self, hours_block):
        al_pool = self.pool.get('account.analytic.line')
        al_ids = al_pool.search(self.cr, self.uid,
                               [['invoice_id', '=', hours_block.invoice_id.id]],
                               order='date desc')
        res = al_pool.browse(self.cr, self.uid, al_ids)
        return res

    def _get_and_change_date_format_for_swiss(self, date_to_format):
        date_formatted = ''
        if date_to_format:
            date_formatted = strptime(date_to_format, '%Y-%m-%d').strftime('%d.%m.%Y')
        return date_formatted

report_sxw.report_sxw('report.account.hours.block', 'account.hours.block', 'addons/analytic_hours_block/report/hours_block.rml', parser=account_hours_block)
