# Copyright 2019 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProjectCategory(TransactionCase):
    def test_complete_name(self):
        cat = self.env['project.type'].create({
            'name': 'General'
        })

        self.assertEqual(cat.complete_name, 'General')

        cat2 = self.env['project.type'].create({
            'name': 'Discussion',
            'parent_id': cat.id
        })

        self.assertEqual(cat2.complete_name, 'General / Discussion')
