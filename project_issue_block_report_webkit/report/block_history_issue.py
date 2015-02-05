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
from lxml import html
from lxml.html.clean import Cleaner


class project_issue_history(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(project_issue_history, self).__init__(cr, uid,
                                                    name, context=context)
        self.localcontext.update(
            {'time': time,
             'date_format': DEFAULT_SERVER_DATE_FORMAT,
             'get_related_issue': self._get_related_issue,
             'get_issue_message': self._get_issue_message
             })
        self.context = context

    def _get_related_block_issue(self, hours_block_id):
        project_obj = self.pool['project.project']
        issue_obj = self.pool['project.issue']
        hours_block_obj = self.pool['account.hours.block']
        account_invoice_line_obj = self.pool['account.invoice.line']
        hours_block = hours_block_obj.browse(self.cr, self.uid,
                                             hours_block_id.id,
                                             context=self.context)
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
        issue_ids = issue_obj.search(self.cr, self.uid,
                                     [('project_id',
                                       'in',
                                       project_ids)], context=self.context)

        return issue_obj.browse(self.cr, self.uid,
                                issue_ids,
                                context=self.context)

    def _get_related_issue(self, current_issue):
        if self.context['active_model'] == 'account.hours.block':
            '''
            We call this report from a project,
            so we do not need to search the related project
            '''
            return self._get_related_block_issue(current_issue)
        else:
            return current_issue

    def _get_issue_message(self, project_issue):
        message = []
        mail_message_obj = self.pool['mail.message']
        message_ids = mail_message_obj.search(self.cr, self.uid,
                                              [('res_id', '=',
                                                project_issue.id),
                                               ('model', '=', 'project.issue'),
                                               ('type', '=', 'email')],
                                              order='date desc',
                                              context=self.context)
        cleaner = Cleaner(style=True, links=True,
                          add_nofollow=True,
                          page_structure=False,
                          safe_attrs_only=False)
        for mes in mail_message_obj.browse(self.cr, self.uid,
                                           message_ids,
                                           context=self.context):
            doc = html.document_fromstring(mes.body)
            doc = cleaner.clean_html(doc)
            value_body = html.tostring(doc)
            messi = {'date': mes.date,
                     'subject': mes.subject,
                     'body': value_body
                     }
            message.append(messi)
        return message

report_sxw.report_sxw(
    'report.report_history_issue_block',
    'account.hours.block',
    'addons/project_issue_block_report_webkit/report/block_history_issue.mako',
    parser=project_issue_history)

report_sxw.report_sxw(
    'report.report_history_issue',
    'project.issue',
    'addons/project_issue_block_report_webkit/report/block_history_issue.mako',
    parser=project_issue_history)
