# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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
    qty = fields.Float(
        string='Quantity',
        default=1,
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
        string='Cost Price'
    )
    price_total = fields.Float(
        compute='_get_price_total',
        string='Total Cost'
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
            description = product.name_get()[0][1]
            uom_id = product.uom_id.id
            unit_price = product.standard_price
        if product.description_sale:
            description += '\n' + product.description_sale
        self.description = description
        self.uom_id = uom_id
        self.unit_price = unit_price

    @api.one
    @api.onchange('uom_id', 'qty')
    def product_uom_change(self):
        unit_price = 0
        qty_uom = 0
        product_uom = self.env['product.uom']
        if self.qty != 0:
            qty_uom = product_uom._compute_qty(
                self.uom_id.id, self.qty, self.product_id.uom_id.id) / self.qty
        if not self.uom_id:
            self.sale_price_unit = 0.0
            return
        if self.product_id:
            unit_price = self.product_id.standard_price
        if self.uom_id and unit_price:
            self.unit_price = unit_price * qty_uom

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
        domain=[('sale_ok', '=', True)],
        required=False
    )
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='UoM',
        required=True
    )
    qty = fields.Float(
        string='Quantity',
        store=True,
        default=1,
    )
    resource_ids = fields.One2many(
        comodel_name='business.requirement.resource',
        inverse_name='business_requirement_deliverable_id',
        string='Business Requirement Resource',
        copy=True,
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
        string='Total revenue',
    )
    linked_project = fields.Many2one(
        string='Linked project',
        comodel_name='project.project',
        groups='project.group_project_manager',
        states={'draft': [('readonly', False)]}
    )
    project_id = fields.Many2one(
        string='Master Project',
        comodel_name='project.project',
        related='business_requirement_id.project_id',
        store=True,
    )
    tax_ids = fields.Many2many(
        'account.tax',
        string='Taxes')

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
        tax_ids = False
        if product:
            description = product.name_get()[0][1]
            uom_id = product.uom_id.id
            unit_price = product.list_price
            tax_ids = product.taxes_id
        if product.description_sale:
            description += '\n' + product.description_sale
        if self.business_requirement_id.project_id.pricelist_id and \
                self.business_requirement_id.partner_id and self.uom_id:
            product = self.product_id.with_context(
                lang=self.business_requirement_id.partner_id.lang,
                partner=self.business_requirement_id.partner_id.id,
                quantity=self.qty,
                pricelist=self.business_requirement_id.
                project_id.pricelist_id.id,
                uom=self.uom_id.id,
            )
            unit_price = product.price
        self.description = description
        self.uom_id = uom_id
        self.unit_price = unit_price
        self.tax_ids = tax_ids

    @api.onchange('uom_id', 'qty')
    def product_uom_change(self):
        if not self.uom_id:
            self.price_unit = 0.0
            return
        if self.business_requirement_id.project_id.pricelist_id and \
                self.business_requirement_id.partner_id:
            product = self.product_id.with_context(
                lang=self.business_requirement_id.partner_id.lang,
                partner=self.business_requirement_id.partner_id.id,
                quantity=self.qty,
                pricelist=self.business_requirement_id.
                project_id.pricelist_id.id,
                uom=self.uom_id.id,
            )
            self.unit_price = product.price


class BusinessRequirement(models.Model):
    _inherit = "business.requirement"

    deliverable_lines = fields.One2many(
        comodel_name='business.requirement.deliverable',
        inverse_name='business_requirement_id',
        string='Deliverable Lines',
        copy=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    total_revenue = fields.Float(
        compute='_compute_deliverable_total',
        string='Total Revenue',
        store=True
    )

    @api.one
    @api.depends(
        'deliverable_lines'
    )
    def _compute_deliverable_total(self):
        if self.deliverable_lines:
            self.total_revenue = sum(
                line.price_total for line in self.deliverable_lines)
