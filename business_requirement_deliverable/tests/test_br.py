# -*- coding: utf-8 -*-
from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class BusinessRequirementTestCase(common.TransactionCase):
    def setUp(self):
        super(BusinessRequirementTestCase, self).setUp()
        self.br = self.registry['business.requirement']

    def test_get_resource_time_total(self):
        vals = {
            'name': ' test',
            'description': 'test',
            'deliverable_lines': [
                (0, 0, {'description': 'line1', 'resource_time': 15.0}),
                (0, 0, {'description': 'line2', 'resource_time': 25.0}),
                (0, 0, {'description': 'line3', 'resource_time': 35.0}),
                (0, 0, {'description': 'line4', 'resource_time': 45.0}),
            ]
        }
        br_id = self.br.create(self.cr, self.uid, vals)
        br_obj = self.br.browse(self.cr, self.uid, br_id)
        br_obj.resource_time_total
        # br._get_resource_time_total()
        time_total = br_obj.resource_time_total
        self.assertEqual(time_total, 15.0 + 25.0 + 35.0 + 45.0)
