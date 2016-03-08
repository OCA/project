# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessRequirementResource(models.Model):
    _inherit = "business.requirement.resource"

    sale_price_unit = fields.Float(
        string='Sales Price',
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
        for resource in self:
            resource.sale_price_total = resource.sale_price_unit * resource.qty

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        super(BusinessRequirementResource, self).product_id_change()
        for resource in self:
            deliverable_project = \
                resource.business_requirement_deliverable_id.project_id
            if deliverable_project.pricelist_id and \
                    deliverable_project.partner_id and resource.uom_id:
                product = resource.product_id.with_context(
                    lang=deliverable_project.partner_id.lang,
                    partner=deliverable_project.partner_id.id,
                    quantity=resource.qty,
                    pricelist=deliverable_project.pricelist_id.id,
                    uom=resource.uom_id.id,
                )
                resource.sale_price_unit = product.price

    @api.multi
    @api.onchange('uom_id', 'qty')
    def product_uom_change(self):
        super(BusinessRequirementResource, self).product_uom_change()
        for resource in self:
            if not resource.uom_id:
                resource.sale_price_unit = 0.0
                return
            deliverable_project = \
                resource.business_requirement_deliverable_id.project_id
            if deliverable_project.pricelist_id and \
                    deliverable_project.partner_id:
                product = resource.product_id.with_context(
                    lang=deliverable_project.partner_id.lang,
                    partner=deliverable_project.partner_id.id,
                    quantity=resource.qty,
                    pricelist=deliverable_project.pricelist_id.id,
                    uom=resource.uom_id.id,
                )
                resource.sale_price_unit = product.price


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
        for br in self:
            if br.deliverable_lines:
                br.resource_tasks_total = sum(
                    br.mapped('deliverable_lines').mapped(
                        'resource_ids').filtered(
                        lambda r: r.resource_type == 'task').mapped(
                            'price_total')
                )

    @api.multi
    @api.depends(
        'deliverable_lines'
    )
    def _compute_resource_procurement_total(self):
        for br in self:
            if br.deliverable_lines:
                br.resource_procurement_total = sum(
                    br.mapped('deliverable_lines').mapped(
                        'resource_ids').filtered(
                        lambda r: r.resource_type == 'procurement').mapped(
                        'price_total'))

    @api.multi
    @api.depends(
        'total_revenue',
        'resource_tasks_total',
        'resource_procurement_total')
    def _compute_gross_profit(self):
        for br in self:
            br.gross_profit = br.total_revenue - \
                br.resource_tasks_total - br.resource_procurement_total
