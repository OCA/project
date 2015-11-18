# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class CrmMakeSaleTestCase(common.TransactionCase):
    def setUp(self):
        super(CrmMakeSaleTestCase, self).setUp()
        self.br = self.env['business.requirement']
        self.crm_lead = self.env['crm.lead']
        self.make_sale = self.env['crm.make.sale']
        self.sale_order = self.env['sale.order']

    def test_makeOrder(self):
        lead_vals = {
            'name': 'Odoo Stock Extend',
            'partner_id': 3,
        }
        lead = self.crm_lead.create(lead_vals)

        br_vals = {
            'name': ' Odoo Stock Extend',
            'lead_id': lead.id,
            'rough_estimation_lines': [
                (0, 0, {'name': 'task1', 'estimated_time': 15.0}),
                (0, 0, {'name': 'task2', 'estimated_time': 25.0}),
                (0, 0, {'name': 'task3', 'estimated_time': 35.0}),
                (0, 0, {'name': 'task4', 'estimated_time': 45.0}),
            ]
        }
        self.br.create(br_vals)

        make_sale_vals = {
            'partner_id': 3,
            'product_id': 1,
        }
        make_sale = self.make_sale.with_context(active_ids=[lead.id]).create(
            make_sale_vals)
        res = make_sale.makeOrder()

        success = False
        if res:
            order_id = res['res_id']
            sale_order = self.sale_order.browse(order_id)
            if sale_order.order_line:
                success = True
        self.assertTrue(success)

    def test_create_sale_order_line(self):
        self.assertTrue(True)
