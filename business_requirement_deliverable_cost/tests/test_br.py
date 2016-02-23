# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


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
        # self.resource = self.env['business.requirement.resource'].create({
        #     'product_id': 1,
        #     'resource_type': 'procurement',
        #     'sale_price_unit': 10,
        #     'qty': 2,
        #     'business_requirement_deliverable_id': 100,
        #     'uom_id': 1,
        #     'description': 'Resource A',
        # })
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
                'lst_price': 1000, 'uom_po_id': self.uom_hours.id})
        self.productB = self.ProductObj.create(
            {'name': 'Product B', 'uom_id': self.uom_hours.id,
                'lst_price': 3000, 'uom_po_id': self.uom_hours.id})
        self.productC = self.ProductObj.create(
            {'name': 'Product C', 'uom_id': self.uom_days.id,
                'uom_po_id': self.uom_days.id})
        self.productD = self.ProductObj.create(
            {'name': 'Product D', 'uom_id': self.uom_kg.id,
                'uom_po_id': self.uom_kg.id})

        self.pricelistA = self.env['product.pricelist'].create({
            'name': 'Pricelist A',
            'type': 'sale',
            'version_id': [
                (0, 0, {
                    'name': 'Version A',
                    'items_id': [(0, 0, {
                        'name': 'Item A',
                        'product_id': self.productA.id,
                        'price_discount': '-0.5',
                    })]
                })
            ]
        })
        self.project = self.env['project.project'].create({
            'name': 'Project A', 'pricelist_id': self.pricelistA.id,
            'partner_id': 3,
        })
        vals = {
            'name': ' test',
            'description': 'test',
            'project_id': self.project.id,
            'partner_id': 3,
            'deliverable_lines': [
                (0, 0, {'description': 'deliverable line1', 'qty': 1.0,
                        'unit_price': 900, 'uom_id': 1,
                        'resource_ids': [
                            (0, 0, {
                                'description': 'Resource Line2',
                                'product_id': self.productA.id,
                                'qty': 100,
                                'uom_id': self.uom_hours.id,
                                'unit_price': 500,
                                'resource_type': 'task',
                                'task_name': 'task 1'
                            }),
                            (0, 0, {
                                'description': 'Resource Line1',
                                'product_id': self.productA.id,
                                'qty': 100,
                                'uom_id': self.uom_hours.id,
                                'unit_price': 500,
                                'resource_type': 'task',
                                'task_name': 'task 2',
                                'sale_price_unit': 400,
                            }),
                            (0, 0, {
                                'description': 'Resource Line3',
                                'product_id': self.productA.id,
                                'qty': 100,
                                'uom_id': self.uom_hours.id,
                                'unit_price': 500,
                                'resource_type': 'procurement',
                                'sale_price_unit': 100,
                            }),
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

    def test_compute_sale_price_total(self):
        """ Checks if the _compute_sale_price_total works properly
        """
        resource = self.env['business.requirement.resource'].search([
            ('description', '=', 'Resource Line1')])
        self.assertEqual(
            resource.sale_price_total, 40000)

    def test_product_id_change(self):
        """ Checks if the product_id_change works properly
        """
        resource = self.env['business.requirement.resource'].search([
            ('description', '=', 'Resource Line1')])
        resource.product_id_change()
        self.assertEqual(
            resource.sale_price_unit, 0)

    def test_compute_resource_tasks_total(self):
        """ Checks if the _compute_resource_tasks_total works properly
        """
        self.assertEqual(
            self.br.resource_tasks_total, 100000.0)

    def test_compute_resource_procurement_total(self):
        """ Checks if the _compute_resource_procurement_total works properly
        """
        self.assertEqual(
            self.br.resource_procurement_total, 50000.0)

    def test_compute_gross_profit(self):
        """ Checks if the _compute_gross_profit works properly
        """
        self.assertEqual(
            self.br.gross_profit, -145200.00)
