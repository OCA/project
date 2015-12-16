# -*- coding: utf-8 -*-
from openerp import api, fields, models


class BusinessRequirement(models.Model):
    _inherit = "business.requirement"

    lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Opportunity'
    )


class CrmLead(models.Model):
    _inherit = "crm.lead"

    resource_cost_total = fields.Float(
        compute='_get_resource_cost_total',
        string='Total resource Cost',
    )

    @api.one
    def _get_resource_cost_total(self):
        cost_total = 0
        linked_brs = self.env['business.requirement'].search(
            [('lead_id', '=', self.id)])
        for br in linked_brs:
            if br.state in ('drop', 'cancel'):
                continue
            cost_total += br.resource_cost_total
        self.resource_cost_total = cost_total


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
            if br.state in ('drop', 'cancel'):
                continue
            for br_line in br.deliverable_lines:
                vals = {
                    'order_id': order_id,
                    'product_id': br_line.product_id.id,
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
