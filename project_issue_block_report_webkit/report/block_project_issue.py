# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Vincent Renaville, ported by Joel Grand-Guillaume
#    Copyright 2010-2013 Camptocamp SA
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


class account_block_ticket(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(account_block_ticket, self).__init__(cr, uid,
                                                   name, context=context)
        self.localcontext.update(
            {'time': time,
             'date_format': DEFAULT_SERVER_DATE_FORMAT,
             'get_related_projects': self._get_related_projects,
             'get_related_issue': self._get_related_issue
             })
        self.context = context

    def _get_related_projects(self, hours_block):
        if self.context['active_model'] == 'project.project':
            '''
            We call this report from a project,
            so we do not need to search the related project
            '''
            return hours_block
        project_obj = self.pool['project.project']
        account_invoice_line_obj = self.pool['account.invoice.line']
        invoice_ids = [x.invoice_id.id for x in hours_block]
        invoice_ids = list(set(invoice_ids))
        ail_ids = account_invoice_line_obj.search(self.cr, self.uid,
                                                  [('invoice_id', 'in',
                                                    invoice_ids)],
                                                  context=self.context)
        ail_records = account_invoice_line_obj.browse(self.cr,
                                                      self.uid, ail_ids,
                                                      context=self.context)
        account_ids = [x.account_analytic_id.id for x in ail_records]
        project_ids = project_obj.search(self.cr, self.uid,
                                         [('analytic_account_id',
                                           'in',
                                           account_ids)], context=self.context)
        return project_obj.browse(self.cr, self.uid,
                                  project_ids,
                                  context=self.context)

    def _get_related_issue(self, current_project, limit_section=30):
        project_issue_obj = self.pool['project.issue']
        result = []
        for type in current_project.type_ids:
            if type.state == 'done':
                color = '#98FB98'
            else:
                limit_section = None
                color = '#FF6347'
            result_issue_ids = project_issue_obj.search(
                self.cr, self.uid,
                [('stage_id', '=', type.id),
                 ('project_id', '=', current_project.id)],
                limit=limit_section,
                order='create_date desc',
                context=self.context)
            result_ids_records = project_issue_obj.browse(self.cr, self.uid,
                                                          result_issue_ids,
                                                          context=self.context)
            result_records = {
                'type': type,
                'issues': result_ids_records,
                'color': color,
                }
            result.append(result_records)

        print str(result)
        return result


report_sxw.report_sxw(
    'report.report_ticket_block_project',
    'account.hours.block',
    'addons/project_issue_block_report_webkit/report/block_project_issue.mako',
    parser=account_block_ticket)

report_sxw.report_sxw(
    'report.report_ticket_block_project_from_project',
    'project.project',
    'addons/project_issue_block_report_webkit/report/block_project_issue.mako',
    parser=account_block_ticket)
