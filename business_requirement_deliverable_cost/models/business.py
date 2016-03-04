# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessRequirementResource(models.Model):
    _inherit = "business.requirement.resource"

    sale_price_unit = fields.Float(
        string='Sales Price',
        readonly=True,
        groups='business_requirement_deliverable_cost.\
group_business_requirement_estimation',
    )
    sale_price_total = fields.Float(
        compute='_compute_sale_price_total',
        string='Total Revenue',
        groups='business_requirement_deliverable_cost.\
group_business_requirement_estimation',
    )
    unit_price = fields.Float(
        groups='business_requirement_deliverable_cost.\
group_business_requirement_cost_control',
    )
    price_total = fields.Float(
        groups='business_requirement_deliverable_cost.\
group_business_requirement_cost_control',
    )

    @api.multi
    @api.depends('sale_price_unit', 'qty')
    def _compute_sale_price_total(self):
        self.ensure_one()
        self.sale_price_total = self.sale_price_unit * self.qty

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        self.ensure_one()
        super(BusinessRequirementResource, self).product_id_change()
        if self.business_requirement_deliverable_id. \
            project_id.pricelist_id and \
                self.business_requirement_deliverable_id. \
                project_id.partner_id and self.uom_id:
            product = self.product_id.with_context(
                lang=self.business_requirement_deliverable_id.
                project_id.partner_id.lang,
                partner=self.business_requirement_deliverable_id.
                project_id.partner_id.id,
                quantity=self.qty,
                pricelist=self.business_requirement_deliverable_id.
                project_id.pricelist_id.id,
                uom=self.uom_id.id,
            )
            self.sale_price_unit = product.price

    @api.onchange('uom_id', 'qty')
    def product_uom_change(self):
        if not self.uom_id:
            self.sale_price_unit = 0.0
            return
        if self.business_requirement_deliverable_id. \
            project_id.pricelist_id and \
                self.business_requirement_deliverable_id. \
                project_id.partner_id:
            product = self.product_id.with_context(
                lang=self.business_requirement_deliverable_id.
                project_id.partner_id.lang,
                partner=self.business_requirement_deliverable_id.
                project_id.partner_id.id,
                quantity=self.qty,
                pricelist=self.business_requirement_deliverable_id.
                project_id.pricelist_id.id,
                uom=self.uom_id.id,
            )
            self.sale_price_unit = product.price


class BusinessRequirement(models.Model):
    _inherit = "business.requirement"

    total_revenue = fields.Float(
        store=True,
        groups='business_requirement_deliverable_cost.\
group_business_requirement_estimation',
    )
    resource_tasks_total = fields.Float(
        compute='_compute_resource_tasks_total',
        string='Total tasks',
        store=True,
        groups='business_requirement_deliverable_cost.\
group_business_requirement_cost_control',
    )
    resource_procurement_total = fields.Float(
        compute='_compute_resource_procurement_total',
        string='Total procurement',
        store=True,
        groups='business_requirement_deliverable_cost.\
group_business_requirement_cost_control',
    )
    gross_profit = fields.Float(
        string='Estimated Gross Profit',
        compute='_compute_gross_profit',
        groups='business_requirement_deliverable_cost.\
group_business_requirement_cost_control',
    )

    @api.multi
    @api.depends(
        'deliverable_lines'
    )
    def _compute_resource_tasks_total(self):
        self.ensure_one()
        if self.deliverable_lines:
            self.resource_tasks_total = sum(
                self.mapped('deliverable_lines').mapped(
                    'resource_ids').filtered(
                    lambda r: r.resource_type == 'task').mapped('price_total')
            )

    @api.multi
    @api.depends(
        'deliverable_lines'
    )
    def _compute_resource_procurement_total(self):
        self.ensure_one()
        if self.deliverable_lines:
            self.resource_procurement_total = sum(
                self.mapped('deliverable_lines').mapped(
                    'resource_ids').filtered(
                    lambda r: r.resource_type == 'procurement').mapped(
                    'price_total'))

    @api.multi
    @api.depends(
        'total_revenue',
        'resource_tasks_total',
        'resource_procurement_total')
    def _compute_gross_profit(self):
        self.ensure_one()
        self.gross_profit = self.total_revenue - \
            self.resource_tasks_total - self.resource_procurement_total
