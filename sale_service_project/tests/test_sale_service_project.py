# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestSaleServiceProject(TransactionCase):
    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestSaleServiceProject, self).setUp()

        self.product_template_revision = self.env.ref(
            'sale_service_project.product_template_revision_1')
        self.product_revision = self.env['product.product'].search(
            [('product_tmpl_id', '=', self.product_template_revision.id)])
        self.product_stock = self.env.ref('product.product_product_4')

        self.product_cost_service = self.env.ref(
            'product.product_product_consultant')
        self.sale_order_model = self.env['sale.order']
        self.sale_order_line = self.env['sale.order.line']
        self.partner = self.env.ref('base.res_partner_2')

        self.price_list = self.env.ref('product.list0')

        self.sale_order_manual = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'order_policy': 'manual',
            'pricelist_id': self.price_list.id,
        })
        self.sale_order_line.create(
            {'product_id': self.product_revision.id,
             'product_uos_qty': 1,
             'price_unit': self.product_revision.list_price,
             'order_id': self.sale_order_manual.id,
             'name': self.product_revision.name})

        self.sale_order_analytic = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'order_policy': 'analytic',
            'pricelist_id': self.price_list.id,
        })
        self.sale_order_line.create(
            {'product_id': self.product_revision.id,
             'product_uos_qty': 1,
             'price_unit': self.product_revision.list_price,
             'order_id': self.sale_order_analytic.id,
             'name': self.product_revision.name,
             })

    def test_check_product_price(self):
        res = self.product_template_revision.action_compute_price()
        self.assertEquals(res['res_model'], 'product.price.service.wizard')
        wiz = self.env['product.price.service.wizard']
        price = wiz._compute_price(
            self.product_template_revision, self.product_cost_service)
        self.assertAlmostEqual(price, 170.00)

    def test_sale_change_product(self):
        # Service product with task and materials
        res = self.sale_order_manual.order_line.product_id_change(
            self.price_list.id, self.product_revision.id, 1, False, 0, False,
            '', self.sale_order_manual.partner_id.id, False, True, False,
            False, False, False)
        self.assertEqual(len(res['value']['task_work_ids']), 2)
        self.assertEqual(len(res['value']['task_materials_ids']), 2)

        # Stock product without task and materials
        res = self.sale_order_manual.order_line.product_id_change(
            self.price_list.id, self.product_stock.id, 1, False, 0, False,
            '', self.sale_order_manual.partner_id.id, False, True, False,
            False, False, False)
        self.assertFalse(res['value']['task_work_ids'])
        self.assertFalse(res['value']['task_materials_ids'])

    def test_sale_to_project(self):
        # Confirm the sale order
        self.sale_order_manual.action_button_confirm()

        # Search task generate by sale order
        task = self.env['project.task'].search(
            [('sale_line_id', '=', self.sale_order_manual.order_line[0].id)])
        self.assertTrue(task)
        self.assertTrue(task.project_id)

        # Confirm the sale order
        self.sale_order_analytic.action_button_confirm()

        # Search task generate by sale order
        task = self.env['project.task'].search(
            [('sale_line_id', '=', self.sale_order_analytic.order_line[0].id)])
        self.assertTrue(task)
        self.assertEqual(
            task.project_id.to_invoice,
            self.env.ref('hr_timesheet_invoice.timesheet_invoice_factor1'))
        analytic_lines = task.mapped(
            'work_ids.hr_analytic_timesheet_id.line_id')
        analytic_lines.invoice_cost_create()
        self.assertEqual(len(self.sale_order_analytic.invoice_ids), 1)
