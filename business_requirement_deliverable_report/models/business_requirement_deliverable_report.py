# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.report import report_sxw
from openerp.addons.report_docx.report.report_docx import ReportDocx
import html2text


class BRDeliverableReportDocxParser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(BRDeliverableReportDocxParser, self).__init__(
            cr, uid, name, context=context)


class BRDeliverableReport(ReportDocx):
    def __init__(
        self, name, table, rml=False, parser=False, header=True, store=False
    ):
        super(BRDeliverableReport, self).__init__(
            name, table, rml, parser, header, store
        )

    def generate_docx_data(self, cr, uid, ids, context):
        active_module = context['active_model']

        data = []
        for id in ids:
            module = self.pool.get(active_module).browse(
                cr, uid, id, context)
            data.append(self._obj2dict(module))

        return data

    def _parse_html(self, obj):
        if isinstance(obj, (str, unicode)):
            return html2text.html2text(obj)
        else:
            return obj

    def _obj2dict(self, obj):
        memberlist = [m for m in dir(obj)]
        context = {}
        for m in memberlist:
            if m[0] != "_" and not callable(m):
                context[m] = self._parse_html(getattr(obj, m))
        return context

BRDeliverableReport(
    'report.report.docx', 'report.docx.template',
    parser=BRDeliverableReportDocxParser)
