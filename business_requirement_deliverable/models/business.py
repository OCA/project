# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.exceptions import ValidationError
from openerp.tools.translate import _


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
    task_name = fields.Char('Task name')
    business_requirement_deliverable_id = fields.Many2one(
        comodel_name='business.requirement.deliverable',
        string='Business Requirement Deliverable',
        ondelete='cascade'
    )
    unit_price = fields.Float(
        string='Sales Price'
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
            unit_price = product.standard_price
        self.description = description
        self.uom_id = uom_id
        self.unit_price = unit_price

    @api.one
    @api.onchange('resource_type')
    def resource_type_change(self):
        if self.resource_type == 'procurement':
            self.user_id = False

    @api.one
    @api.constrains('resource_type', 'uom_id')
    def _check_description(self):
        if self.resource_type == 'task'\
                and self.uom_id.category_id.name != 'Working Time':
            raise ValidationError(_(
                "When resource type is task, the uom category should be time"))


class BusinessRequirementDeliverable(models.Model):
    _name = "business.requirement.deliverable"
    _description = "Business Requirement Deliverable"

    sequence = fields.Integer('Sequence')
    description = fields.Text('Description', required=True)
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
        string='Sales Price'
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
        string='Total Revenue',
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
