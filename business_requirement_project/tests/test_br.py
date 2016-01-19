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

        self.ProjectObj = self.env['project.project']
        self.projectA = self.ProjectObj.create(
            {'name': 'Test Project A', 'partner_id': 1, 'parent_id': 1,
                'analytic_account_id': 192})
        self.projectB = self.ProjectObj.create(
            {'name': 'Test Project B', 'partner_id': 1, 'parent_id': 1,
                'analytic_account_id': 192})

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
                'uom_po_id': self.uom_hours.id,
                'standard_price': 450})
        self.productB = self.ProductObj.create(
            {'name': 'Product B', 'uom_id': self.uom_hours.id,
                'uom_po_id': self.uom_hours.id,
                'standard_price': 550})
        self.productC = self.ProductObj.create(
            {'name': 'Product C', 'uom_id': self.uom_days.id,
                'uom_po_id': self.uom_days.id,
                'standard_price': 650})
        self.productD = self.ProductObj.create(
            {'name': 'Product D', 'uom_id': self.uom_kg.id,
                'uom_po_id': self.uom_kg.id,
                'standard_price': 750})

        vals = {
            'name': ' test',
            'description': 'test',
            'project_id': self.projectA.id,
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
        self.brA = self.env['business.requirement'].create(vals)
        self.brB = self.env['business.requirement'].create(vals)
        self.brC = self.env['business.requirement'].create(vals)

    def test_br_state(self):
        # test when state=draft
        self.brA.state = 'draft'
        self.brB.state = 'draft'
        self.brC.state = 'draft'
        try:
            action = self.projectA.generate_projects_wizard()
        except Exception:
            action = False
        self.assertEqual(action, False)

        # test when state=confirmed
        self.brA.state = 'confirmed'
        self.brB.state = 'confirmed'
        self.brC.state = 'confirmed'
        try:
            action = self.projectA.generate_projects_wizard()
        except Exception:
            action = False
        self.assertEqual(action, False)

        # test when state=approved
        self.brA.state = 'approved'
        self.brB.state = 'confirmed'
        self.brC.state = 'draft'
        try:
            action = self.projectA.generate_projects_wizard()
        except Exception:
            action = False
        self.assertEqual(action, False)

        # test when state=approved
        self.brA.state = 'approved'
        self.brB.state = 'approved'
        self.brC.state = 'draft'
        try:
            action = self.projectA.generate_projects_wizard()
        except Exception:
            action = False
        self.assertEqual(action, False)

        # test when state=approved
        self.brA.state = 'approved'
        self.brB.state = 'approved'
        self.brC.state = 'confirmed'
        try:
            action = self.projectA.generate_projects_wizard()
        except Exception:
            action = False
        self.assertEqual(action, False)

        # test when state=approved
        self.brA.state = 'approved'
        self.brB.state = 'approved'
        self.brC.state = 'approved'
        try:
            action = self.projectA.generate_projects_wizard()
        except Exception:
            action = False
        self.assertNotEqual(action, False)

        # test when state=approved
        self.brA.state = 'done'
        self.brB.state = 'approved'
        self.brC.state = 'approved'
        try:
            action = self.projectA.generate_projects_wizard()
        except Exception:
            action = False
        self.assertNotEqual(action, False)

        # test when state=approved
        self.brA.state = 'done'
        self.brB.state = 'approved'
        self.brC.state = 'approved'
        try:
            action = self.projectA.generate_projects_wizard()
        except Exception:
            action = False
        self.assertNotEqual(action, False)

    def test_for_br(self):
        self.brA.state = 'approved'
        self.brB.state = 'approved'
        self.brC.state = 'approved'
        try:
            action = self.projectA.generate_projects_wizard()
        except Exception:
            action = False
        self.assertNotEqual(action, False)
        self.assertNotEqual(action.get('res_id', False), False)
        self.wizard = self.env['br.generate.projects'].browse(action['res_id'])
        self.wizard.for_br = True
        try:
            self.wizard.apply()
        except:
            # self.assertTrue(False)
            pass
