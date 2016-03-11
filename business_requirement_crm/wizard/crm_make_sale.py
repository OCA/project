# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.osv import osv


class CrmMakeSale(models.TransientModel):
    _name = "br.crm.make.sale"
    _inherit = "crm.make.sale"

    update_quotation = fields.Boolean('Update existing quotation')

    @api.multi
    def make_orderline(self):
        context = self.env.context
        case_id = context and context.get('active_ids', []) or []
        case_id = case_id and case_id[0] or False
        res = {}
        if not self.update_quotation:
            res = super(CrmMakeSale, self).makeOrder()
        else:
            saleorder = self.env['sale.order'].search([
                ('origin', '=', _('Opportunity: %s') % str(case_id))])
            saleorder = saleorder and saleorder[0] or False
            if saleorder:
                res = {'res_id': saleorder.id}
                if saleorder.order_line:
                    saleorder.order_line.unlink()

        order_id = res.get('res_id', False)
        if order_id:
            order_lines = self.prepare_sale_order_line(case_id, order_id)
            self.create_sale_order_line(order_lines)
        return res

    def prepare_sale_order_line(self, case_id, order_id):
        lines = []
        case = self.env['crm.lead'].browse(case_id)
        linked_brs = case.project_id and case.project_id.br_ids or []
        if not linked_brs:
            raise osv.except_osv(
                _('Error!'),
                _("""There is no available business requirement to
                    make sale order!"""))
        for br in linked_brs:
            if br.state in ('drop', 'cancel'):
                continue
            for br_line in br.deliverable_lines:
                vals = {
                    'order_id': order_id,
                    'product_id': br_line.product_id.id,
                    'tax_id': br_line.tax_ids,
                    'name': br_line.description,
                    'product_uom_qty': br_line.qty,
                    'product_uos_qty': br_line.qty,
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
