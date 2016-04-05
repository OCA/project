# -*- coding: utf-8 -*-

from openerp.tests import common
import openerp
from openerp.addons.report_docx_module.models.parser \
    import BRDeliverableReport, BRDeliverableReportDocxParser


class TestBRDeliverableReport(common.TransactionCase):
    def setUp(self):
        super(TestBRDeliverableReport, self).setUp()

    def test_generate_docx_data(self):
        report = BRDeliverableReport(
            'report.report.test', 'report.docx.template',
            parser=BRDeliverableReportDocxParser
        )

        attributes = [
            'name', 'users', 'model_access',
            'rule_groups', 'menu_access', 'view_access', 'comment',
            'category_id', 'color', 'full_name', 'share'
        ]

        pool = openerp.registry(self.cr.dbname)
        report.pool = pool
        context = {
            'active_model': 'res.groups'
        }

        data = report.generate_docx_data(self.cr, 1, [1], context)[0]

        res_groups = self.registry('res.groups').browse(self.cr, 1, [1])

        for attribute in attributes:
            self.assertEqual(data[attribute], res_groups[attribute])
