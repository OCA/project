# -*- coding: utf-8 -*-
# © 2015
# Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class BusinessRequirementTestCase(common.TransactionCase):
    def setUp(self):
        super(BusinessRequirementTestCase, self).setUp()
        self.br = self.registry['business.requirement']

    def test_get_resource_cost_total(self):
        vals = {
            'name': ' test',
            'description': 'test',
            'deliverable_lines': [
                (
                    0, 0,
                    {
                        'description': 'line1',
                        'unit_price': 1,
                        'qty': 15,
                    }
                ),
                (
                    0, 0,
                    {
                        'description': 'line1',
                        'unit_price': 1,
                        'qty': 25,
                    }
                ),
                (
                    0, 0,
                    {
                        'description': 'line1',
                        'unit_price': 1,
                        'qty': 35,
                    }
                ),
                (
                    0, 0,
                    {
                        'description': 'line1',
                        'unit_price': 1,
                        'qty': 45,
                    }
                ),
            ]
        }
        br = self.br.create(vals)
        cost_total = br.resource_cost_total
        self.assertEqual(cost_total, 15 + 25 + 35 + 45)
