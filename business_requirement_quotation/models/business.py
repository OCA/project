# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class CrmMakeSale(models.Model):
    _inherit = "crm.make.sale"

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
        linked_brs = self.env['business.requirement'].search(
            [('lead_id', '=', case_id)])
        for br in linked_brs:
            if br.drop:
                continue
            for br_line in br.deliverable_lines:
                qty = br_line.estimated_time if \
                    br_line.resouce_type == 'time' else br_line.qty
                vals = {
                    'order_id': order_id,
                    'product_id': br_line.product_id.id,
                    'name': br_line.name,
                    'product_uom_qty': qty,
                    'product_uos_qty': qty,
                    'product_uom': br_line.uom_id.id,
                    'product_uos': br_line.uom_id.id,
                    'price_unit': br_line.unit_price,
                }
                lines.append(vals)
        return lines

    def create_sale_order_line(self, order_lines):
        saleorder_line_obj = self.env['sale.order.line']
        for line in order_lines:
            saleorder_line_obj.create(line)
