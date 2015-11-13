# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <AUTHOR(Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class CrmMakeSale(models.Model):
    _inherit = "crm.make.sale"

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        domain="[('type', '=','service')]",
        required=True
    )

    @api.multi
    def makeOrder(self):
        res = super(CrmMakeSale, self).makeOrder()
        context = self.env.context
        case_id = context and context.get('active_ids', []) or []
        order_id = res.get('res_id', False)
        if order_id:
            order_lines = self.prepare_sale_order_line(case_id, order_id)
            self.create_sale_order_line(order_lines)
        return res

    def prepare_sale_order_line(self, case_id, order_id):
        lines = []
        case_obj = self.env['crm.lead']
        case = case_obj.browse(case_id)
        for br in case.br_ids:
            if br.drop:
                continue
            for br_line in br.rough_estimation_lines:
                qty = br_line.estimated_time
                vals = {
                    'order_id': order_id,
                    'product_id': self.product_id.id,
                    'name': br_line.name,
                    'product_uom_qty': qty,
                    'product_uos_qty': qty,
                    'price_unit': br_line.unit_price,
                }
                lines.append(vals)
        return lines

    def create_sale_order_line(self, order_lines):
        saleorder_line_obj = self.env['sale.order.line']
        for line in order_lines:
            saleorder_line_obj.create(line)
