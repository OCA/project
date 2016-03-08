# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestDefaultResourcesFromProduct(common.TransactionCase):
    def setUp(self):
        super(TestDefaultResourcesFromProduct, self).setUp()

        self.brd_a = \
            self.env['business.requirement.deliverable'].create(
                {'uom_id': 5,
                 'description': 'Test A',
                 })

        self.brd_b = \
            self.env['business.requirement.deliverable'].create(
                {'uom_id': 5,
                 'description': 'Test B',
                 })

        # Common resource_lines
        self.rl_lines = [
            (0, 0, {'resource_type': 'task',
                    'product_id': 26,
                    'uom_id': 5,
                    'task_categ_id': 1,
                    'task_name': 'Task A',
                    'description': 'Test B',
                    }),
            (0, 0, {'resource_type': 'task',
                    'product_id': 27,
                    'uom_id': 5,
                    'task_categ_id': 2,
                    'task_name': 'Task B',
                    'description': 'Test B',
                    }),
            (0, 0, {'resource_type': 'procurement',
                    'product_id': 26,
                    'uom_id': 5,
                    'task_categ_id': 1,
                    'description': 'Test B',
                    })]

        # Search product and set up product_template with resource_lines
        self.product = self.env['product.product'].search(
            [('id', '=', '9')])
        self.product.product_tmpl_id.resource_lines = self.rl_lines
        # Assing the product to the br_deriverable
        self.brd_a.product_id = self.product.id
        self.brd_a.resource_ids = self.rl_lines

    def test_prepare_resouce_lines(self):
        self.brd_b.product_id = self.product.id
        self.brd_b.resource_ids = self.brd_b._prepare_resouce_lines()
        self.assertEqual(self.brd_a.resource_ids, self.brd_b.resource_ids)
