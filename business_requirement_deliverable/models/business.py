# -*- coding: utf-8 -*-
# © 2015 Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessRequirementResource(models.Model):
    _name = "business.requirement.resource"
    _description = "Business Requirement Resource"

    sequence = fields.Integer('Sequence')
    description = fields.Char('Description', required=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=False
    )
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='UoM',
        required=True
    )
    qty = fields.Integer(
        string='Quantity'
    )
    resource_time = fields.Integer(
        string='Resouce Time'
    )
    resource_type = fields.Selection(
        selection=[('task', 'Task'), ('procurement', 'Procurement')],
        string='Type',
        required=True,
        default='procurement'
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assign To',
        ondelete='set null'
    )
    business_requirement_deliverable_id = fields.Many2one(
        comodel_name='business.requirement.deliverable',
        string='Business Requirement Deliverable',
        ondelete='cascade'
    )
    unit_price = fields.Float(
        string='Unit Price'
    )
    price_total = fields.Float(
        compute='_get_price_total',
        string='Subtotal'
    )

    @api.one
    @api.depends('resource_time', 'unit_price', 'qty')
    def _get_price_total(self):
        if self.resource_type == "task":
            self.price_total = self.unit_price * self.resource_time
        else:
            self.price_total = self.unit_price * self.qty

    @api.one
    @api.onchange('product_id')
    def product_id_change(self):
        description = ''
        uom_id = False
        unit_price = 0
        product = self.product_id
        if product:
            description = product.name
            uom_id = product.uom_id.id
            unit_price = product.list_price
        self.description = description
        self.uom_id = uom_id
        self.unit_price = unit_price

    @api.one
    @api.onchange('resource_type')
    def resouce_type_change(self):
        if self.resource_type == "task":
            self.qty = 0
        elif self.resource_type == "procurement":
            self.resource_time = 0

    @api.one
    def write(self, vals):
        resource_type = vals.get('resource_type', False)
        if resource_type == "procurement":
            vals.update({'resource_time': 0})
        elif resource_type == "task":
            vals.update({'qty': 0})
        return super(BusinessRequirementResource, self).write(vals)


class BusinessRequirementDeliverable(models.Model):
    _name = "business.requirement.deliverable"
    _description = "Business Requirement Deliverable"

    sequence = fields.Integer('Sequence')
    description = fields.Char('Description', required=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=False
    )
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='UoM',
        required=True
    )
    qty = fields.Integer(
        string='Quantity',
        store=True,
        default=1,
    )
    resource_ids = fields.One2many(
        comodel_name='business.requirement.resource',
        inverse_name='business_requirement_deliverable_id',
        string='Business Requirement Resource',
        copy=False,
    )
    business_requirement_id = fields.Many2one(
        comodel_name='business.requirement',
        string='Business Requirement',
        ondelete='cascade'
    )
    unit_price = fields.Float(
        string='Unit Price'
    )
    price_total = fields.Float(
        compute='_get_price_total',
        string='Subtotal'
    )

    @api.one
    @api.depends('unit_price', 'qty')
    def _get_price_total(self):
        self.price_total = self.unit_price * self.qty

    @api.one
    @api.onchange('product_id')
    def product_id_change(self):
        description = ''
        uom_id = False
        unit_price = 0
        product = self.product_id
        if product:
            description = product.name
            uom_id = product.uom_id.id
            unit_price = product.list_price
        self.description = description
        self.uom_id = uom_id
        self.unit_price = unit_price


class BusinessRequirement(models.Model):
    _inherit = "business.requirement"

    deliverable_lines = fields.One2many(
        comodel_name='business.requirement.deliverable',
        inverse_name='business_requirement_id',
        string='Deliverable Lines',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    resource_cost_total = fields.Float(
        compute='_get_deliverable_cost_total',
        string='Total Price',
        store=True
    )

    @api.one
    @api.depends(
        'deliverable_lines.price_total'
    )
    def _get_deliverable_cost_total(self):
        cost_total = sum(
            line.price_total for line in self.deliverable_lines)
        self.resource_cost_total = cost_total
