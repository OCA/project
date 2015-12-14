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
        self.br = self.env['business.requirement']

    def test_get_level(self):
        br_vals1 = {
            'name': ' test',
            'description': 'test',
            'parent_id': False,
        }
        br1 = self.br.create(br_vals1)
        br1._get_level()
        level1 = br1.level
        self.assertEqual(level1, 1)

        br_vals2 = {
            'name': ' test',
            'description': 'test',
            'parent_id': br1.id,
        }
        br2 = self.br.create(br_vals2)
        br2._get_level()
        level2 = br2.level
        self.assertEqual(level2, 2)

        br_vals3 = {
            'name': ' test',
            'description': 'test',
            'parent_id': br2.id,
        }
        br3 = self.br.create(br_vals3)
        br3._get_level()
        level3 = br3.level
        self.assertEqual(level3, 3)

    def test_action_button_confirm(self):
        br_vals = {
            'name': ' test',
            'description': 'test',
            'parent_id': False,
        }
        br = self.br.create(br_vals)
        br.action_button_confirm()
        self.assertEqual(br.state, 'confirmed')

    def test_action_button_back_draft(self):
        br_vals = {
            'name': 'test',
            'description': 'test',
            'parent_id': False,
        }
        br = self.br.create(br_vals)
        br.action_button_back_draft()
        self.assertEqual(br.state, 'draft')

    def test_action_button_approve(self):
        br_vals = {
            'name': ' test',
            'description': 'test',
            'parent_id': False,
        }
        br = self.br.create(br_vals)
        br.action_button_approve()
        self.assertEqual(br.state, 'approved')

    def test_action_button_done(self):
        br_vals = {
            'name': ' test',
            'description': 'test',
            'parent_id': False,
        }
        br = self.br.create(br_vals)
        br.action_button_done()
        self.assertEqual(br.state, 'done')
