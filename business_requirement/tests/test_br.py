# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class BusinessRequirementTestCase(common.TransactionCase):
    def setUp(self):
        super(BusinessRequirementTestCase, self).setUp()
        self.br = self.env['business.requirement']

    def test_get_resource_time_total(self):
        vals = {
            'name': ' test',
            'deliverable_lines': [
                (0, 0, {'name': 'line1', 'resource_time': 15.0}),
                (0, 0, {'name': 'line2', 'resource_time': 25.0}),
                (0, 0, {'name': 'line3', 'resource_time': 35.0}),
                (0, 0, {'name': 'line4', 'resource_time': 45.0}),
            ]
        }
        br = self.br.create(vals)
        br._get_resource_time_total()
        time_total = br.resource_time_total
        self.assertEqual(time_total, 15.0 + 25.0 + 35.0 + 45.0)

    def test_compute_level(self):
        br_vals1 = {
            'name': ' test',
            'parent_id': False,
        }
        br1 = self.br.create(br_vals1)
        level1 = br1._compute_level()
        self.assertEqual(level1, 1)

        br_vals2 = {
            'name': ' test',
            'parent_id': br1.id,
        }
        br2 = self.br.create(br_vals2)
        level2 = br2._compute_level()
        self.assertEqual(level2, 2)

        br_vals3 = {
            'name': ' test',
            'parent_id': br2.id,
        }
        br3 = self.br.create(br_vals3)
        level3 = br3._compute_level()
        self.assertEqual(level3, 3)

    def test_action_button_confirm(self):
        br_vals = {
            'name': ' test',
            'parent_id': False,
        }
        br = self.br.create(br_vals)
        br.action_button_confirm()
        self.assertEqual(br.state, 'confirmed')

    def test_action_button_back_draft(self):
        br_vals = {
            'name': 'test',
            'parent_id': False,
        }
        br = self.br.create(br_vals)
        br.action_button_back_draft()
        self.assertEqual(br.state, 'draft')

    def test_action_button_approve(self):
        br_vals = {
            'name': ' test',
            'parent_id': False,
        }
        br = self.br.create(br_vals)
        br.action_button_approve()
        self.assertEqual(br.state, 'approved')

    def test_action_button_done(self):
        br_vals = {
            'name': ' test',
            'parent_id': False,
        }
        br = self.br.create(br_vals)
        br.action_button_done()
        self.assertEqual(br.state, 'done')

    def test_get_states(self):
        br_vals = {
            'name': ' test',
            'parent_id': False,
        }
        br = self.br.create(br_vals)
        states = br._get_states()
        states2 = [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('approved', 'Approved'),
            ('done', 'Done')
        ]
        self.assertEqual(states, states2)
