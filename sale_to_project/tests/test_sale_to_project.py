# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import fields
from openerp.tests import common


class TestSaleToProject(common.TransactionCase):

    def setUp(self):
        super(TestSaleToProject, self).setUp()
        self.sale_to_project_model = self.env['sale.to.project']
        self.sale_line_to_project_model = self.env['sale.line.to.project']
        self.sale_model = self.env['sale.order']
        self.sale_line_model = self.env['sale.order.line']

        self.partner1 = self.env.ref('base.res_partner_2')
        self.product1 = self.env.ref('product.product_product_7')
        self.product2 = self.env.ref('product.product_product_9')
        self.product3 = self.env.ref('product.product_product_11')

        self.sale = self._create_sale([(self.product1, 1000),
                                       (self.product2, 500),
                                       (self.product3, 800)])
        self.sale.action_button_confirm()

    def _create_sale(self, line_products):
        """ Create a sales order.

        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        for product, qty in line_products:
            lines.append(
                (0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': qty,
                    'product_uom': product.uom_id.id,
                    'price_unit': 50,
                })
            )
        return self.sale_model.create({
            'partner_id': self.partner1.id,
            'order_line': lines,
        })

    def test_create_all_lines(self):
        sale = self.sale
        wizard = self.sale_to_project_model.create({
            'create_contract_method': 'all',
        }).with_context(active_ids=sale.ids)
        action = wizard.button_create_contract()
        self.assertEquals(action, {'type': 'ir.actions.act_window_close'})
        contract = sale.contract_ids
        self.assertEquals(len(contract), 1)
        self.assertEquals(contract.partner_id, self.partner1)
        dt_from_str = fields.Datetime.from_string
        d_to_str = fields.Date.to_string
        self.assertEquals(contract.date_start,
                          d_to_str(dt_from_str(sale.date_order)))
        self.assertEquals(contract.code, sale.name)
        self.assertEquals(contract.type, 'contract')
        self.assertTrue(contract.recurring_invoices)
        self.assertEquals(contract.company_id, sale.company_id)
        for sale_line in sale.order_line:
            line = sale_line.recurring_invoice_line_ids
            self.assertEquals(len(line), 1)
            self.assertEquals(line.product_id, sale_line.product_id)
            self.assertEquals(line.name, sale_line.name)
            self.assertEquals(line.quantity, sale_line.product_uom_qty)
            self.assertEquals(line.uom_id, sale_line.product_uom)
            self.assertEquals(line.price_unit, sale_line.price_unit)

            self.assertTrue(sale_line.in_contract)
            self.assertTrue(sale_line.invoiced)  # so no invoice is generated
        # order is done, same behaviour as when we create invoice based
        # on lines selection
        self.assertEquals(sale.state, 'done')

    def test_create_lines_selection(self):
        sale = self.sale
        wizard = self.sale_line_to_project_model.create({})
        selected_lines = sale.order_line[0:2]
        wizard = wizard.with_context(active_ids=selected_lines.ids)
        action = wizard.button_create_contract()
        self.assertEquals(action, {'type': 'ir.actions.act_window_close'})
        contract = sale.contract_ids
        self.assertEquals(len(contract), 1)
        for sale_line in sale.order_line:
            if sale_line in selected_lines:
                line = sale_line.recurring_invoice_line_ids
                self.assertEquals(len(line), 1)
                self.assertEquals(line.product_id, sale_line.product_id)
                self.assertEquals(line.name, sale_line.name)
                self.assertEquals(line.quantity, sale_line.product_uom_qty)
                self.assertEquals(line.uom_id, sale_line.product_uom)
                self.assertEquals(line.price_unit, sale_line.price_unit)

                self.assertTrue(sale_line.in_contract)
                self.assertTrue(sale_line.invoiced)
            else:
                self.assertFalse(sale_line.recurring_invoice_line_ids)
                self.assertFalse(sale_line.in_contract)
                self.assertFalse(sale_line.invoiced)
        self.assertEquals(sale.state, 'manual')
        # if we generate the invoice, only the remaining line should be
        # in the invoice
        sale.action_invoice_create()

        for sale_line in sale.order_line:
            self.assertTrue(sale_line.invoiced)
            if sale_line in selected_lines:
                self.assertTrue(sale_line.in_contract)
                self.assertFalse(sale_line.invoice_lines)
            else:
                self.assertFalse(sale_line.in_contract)
                self.assertTrue(sale_line.invoice_lines)

    def test_create_lines_selection_then_all(self):
        sale = self.sale
        wizard = self.sale_line_to_project_model.create({})
        selected_lines = sale.order_line[0:2]
        wizard = wizard.with_context(active_ids=selected_lines.ids)
        action = wizard.button_create_contract()
        self.assertEquals(action, {'type': 'ir.actions.act_window_close'})
        contract = sale.contract_ids
        self.assertEquals(len(contract), 1)
        for sale_line in sale.order_line:
            if sale_line in selected_lines:
                self.assertTrue(sale_line.recurring_invoice_line_ids)
                self.assertTrue(sale_line.in_contract)
                self.assertTrue(sale_line.invoiced)
            else:
                self.assertFalse(sale_line.recurring_invoice_line_ids)
                self.assertFalse(sale_line.in_contract)
                self.assertFalse(sale_line.invoiced)
        self.assertEquals(sale.state, 'manual')
        # if we generate a new contract, only the remaining line should be
        # in the invoice
        wizard = self.sale_to_project_model.create({
            'create_contract_method': 'all',
        }).with_context(active_ids=sale.ids)
        wizard.button_create_contract()

        for sale_line in sale.order_line:
            self.assertTrue(sale_line.recurring_invoice_line_ids)
            self.assertTrue(sale_line.invoiced)
            self.assertTrue(sale_line.in_contract)
            self.assertFalse(sale_line.invoice_lines)
        self.assertEquals(len(sale.contract_ids), 2)

    def test_all_lines_open_action(self):
        sale = self.sale
        wizard = self.sale_to_project_model.create({
            'create_contract_method': 'all',
        }).with_context(active_ids=sale.ids, open_contract=True)
        action = wizard.button_create_contract()
        expected_keys = {
            'res_id': self.sale.contract_ids.id,
            'views': [(False, 'form')],
            'res_model': 'account.analytic.account'
        }
        for key, value in expected_keys.iteritems():
            self.assertEquals(action.get(key), value)

    def test_lines_selection_open_action(self):
        sale = self.sale
        wizard = self.sale_line_to_project_model.create({})
        selected_lines = sale.order_line[0:2]
        wizard = wizard.with_context(active_ids=selected_lines.ids,
                                     open_contract=True)
        action = wizard.button_create_contract()
        expected_keys = {
            'res_id': self.sale.contract_ids.id,
            'views': [(False, 'form')],
            'res_model': 'account.analytic.account'
        }
        for key, value in expected_keys.iteritems():
            self.assertEquals(action.get(key), value)

    def test_action_open_lines(self):
        sale = self.sale
        wizard = self.sale_to_project_model.create({
            'create_contract_method': 'all',
        }).with_context(active_ids=sale.ids, open_contract=True)
        action = wizard.open_lines()
        expected_keys = {
            'res_model': 'sale.order.line',
            'context': {'search_default_uninvoiced': 1,
                        'search_default_order_id': self.sale.id}
        }
        for key, value in expected_keys.iteritems():
            self.assertEquals(action.get(key), value)
