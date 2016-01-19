# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class BusinessRequirementTestCase(common.TransactionCase):
    def setUp(self):
        super(BusinessRequirementTestCase, self).setUp()
        # self.br = self.registry['business.requirement']
        self.ModelDataObj = self.env['ir.model.data']

        # Configure unit of measure.
        self.categ_wtime = self.ModelDataObj.xmlid_to_res_id(
            'product.uom_categ_wtime')
        self.categ_kgm = self.ModelDataObj.xmlid_to_res_id(
            'product.product_uom_categ_kgm')

        self.UomObj = self.env['product.uom']
        self.uom_hours = self.UomObj.create({
            'name': 'Test-Hours',
            'category_id': self.categ_wtime,
            'factor': 8,
            'uom_type': 'smaller'})
        self.uom_days = self.UomObj.create({
            'name': 'Test-Days',
            'category_id': self.categ_wtime,
            'factor': 1})
        self.uom_kg = self.UomObj.create({
            'name': 'Test-KG',
            'category_id': self.categ_kgm,
            'factor_inv': 1,
            'factor': 1,
            'uom_type': 'reference',
            'rounding': 0.000001})

        # Product Created A, B, C, D
        self.ProductObj = self.env['product.product']
        self.productA = self.ProductObj.create(
            {'name': 'Product A', 'uom_id': self.uom_hours.id,
                'uom_po_id': self.uom_hours.id})
        self.productB = self.ProductObj.create(
            {'name': 'Product B', 'uom_id': self.uom_hours.id,
                'uom_po_id': self.uom_hours.id})
        self.productC = self.ProductObj.create(
            {'name': 'Product C', 'uom_id': self.uom_days.id,
                'uom_po_id': self.uom_days.id})
        self.productD = self.ProductObj.create(
            {'name': 'Product D', 'uom_id': self.uom_kg.id,
                'uom_po_id': self.uom_kg.id})

        vals = {
            'name': ' test',
            'description': 'test',
            'deliverable_lines': [
                (0, 0, {'description': 'deliverable line1', 'qty': 1.0,
                        'unit_price': 900, 'uom_id': 1,
                        'resource_ids': [
                            (0, 0, {
                                'description': 'Resource Line1',
                                'product_id': self.productA.id,
                                'qty': 100,
                                'uom_id': self.uom_hours.id,
                                'unit_price': 500,
                                'resource_type': 'task',
                                'task_name': 'task 1'
                            }),
                            (0, 0, {
                                'description': 'Resource Line1',
                                'product_id': self.productB.id,
                                'qty': 100,
                                'uom_id': self.uom_hours.id,
                                'unit_price': 500,
                                'resource_type': 'task',
                                'task_name': 'task 2'
                            })
                        ]
                        }),
                (0, 0, {'description': 'deliverable line2', 'qty': 1.0,
                        'unit_price': 1100, 'uom_id': 1}),
                (0, 0, {'description': 'deliverable line3', 'qty': 1.0,
                        'unit_price': 1300, 'uom_id': 1}),
                (0, 0, {'description': 'deliverable line4', 'qty': 1.0,
                        'unit_price': 1500, 'uom_id': 1,
                        }),
            ],
        }
        self.br = self.env['business.requirement'].create(vals)

    def test_get_cost_total(self):
        cost_total = self.br.resource_cost_total
        self.assertEqual(
            cost_total, 900.0 * 1 + 1100.0 * 1 + 1300.0 * 1 + 1500.0 * 1)

    def test_get_price_total(self):
        for line in self.br.deliverable_lines:
            if line.description == 'deliverable line1':
                self.assertEqual(line.price_total, 900.0 * 1)
            elif line.description == 'deliverable line2':
                self.assertEqual(line.price_total, 1100.0 * 1)
            elif line.description == 'deliverable line3':
                self.assertEqual(line.price_total, 1300.0 * 1)
            elif line.description == 'deliverable line4':
                self.assertEqual(line.price_total, 1500.0 * 1)

    def test_resource_get_price_total(self):
        for line in self.br.deliverable_lines:
            for resource in line.resource_ids:
                if resource and resource.description == 'Resource Line1':
                    self.assertEqual(resource.price_total, 100 * 500)

    def test_resource_uom_change(self):
        for line in self.br.deliverable_lines:
            for resource in line.resource_ids:
                if resource and resource.resource_type == 'task':
                    try:
                        res = resource.write({'uom_id': self.uom_kg.id})
                    except:
                        res = False
                    self.assertEqual(res, False)
                    break

    def test_resource_product_id_change(self):
        for line in self.br.deliverable_lines:
            for resource in line.resource_ids:
                if resource and resource.description == 'Resource Line1':
                    res = resource.write({'product_id': self.productB.id})
                    if res:
                        self.assertEqual(
                            resource.product_id.id, self.productB.id)
                        self.assertEqual(
                            resource.description, self.productB.name)
                        self.assertEqual(
                            resource.uom_id.id, self.productB.uom_id.id)
                        self.assertEqual(
                            resource.unit_price, self.productB.standard_price)
                    break
