# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


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

    resource_time_total = fields.Float(
        compute='_get_resource_time_total',
        string='Total Resource Time',
        store=True,
    )

    @api.one
    @api.depends(
        'deliverable_lines.resource_time')
    def _get_resource_time_total(self):
        time_total = sum(
            line.resource_time * line.qty for line in self.deliverable_lines)
        self.resource_time_total = time_total


class BusinessRequirementTaskType(models.Model):
    _name = "business.requirement.task.type"
    _description = "Business Requirement Task Type"

    name = fields.Char(string='Name', required=True)


class BusinessRequirementDeliverable(models.Model):
    _name = "business.requirement.deliverable"
    _description = "Business Requirement Deliverable"

    sequence = fields.Integer('Sequence')
    description = fields.Char('Description', required=True)
    business_requirement_id = fields.Many2one(
        comodel_name='business.requirement',
        string='Business Requirement',
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True
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
    resource_time = fields.Float(
        compute='_get_resource_time_total',
        string='Resource Time',
        store=True,
    )
    resource_ids = fields.One2many(
        comodel_name='business.requirement.resource',
        inverse_name='business_requirement_deliverable_id',
        string='Business Requirement Resource',
        copy=False,
    )

    @api.one
    @api.depends(
        'resource_ids.qty',
        'resource_ids.resource_time')
    def _get_resource_time_total(self):
        time_total = sum(
            line.resource_time for line in self.resource_ids)
        self.resource_time = time_total

    @api.one
    @api.onchange('product_id')
    def product_id_change(self):
        uom_id = False
        product = self.product_id
        if product:
            uom_id = product.uom_id.id
        self.uom_id = uom_id


class BusinessRequirementResource(models.Model):
    _name = "business.requirement.resource"
    _description = "Business Requirement Resource"

    sequence = fields.Integer('Sequence')
    description = fields.Char('Description', required=True)
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assign To',
        ondelete='set null'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True
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
        required=True
    )
    task_type = fields.Many2one(
        comodel_name='business.requirement.task.type',
        string='Task Type',
        ondelete='restrict'
    )
    business_requirement_deliverable_id = fields.Many2one(
        comodel_name='business.requirement.deliverable',
        string='Business Requirement Deliverable',
        ondelete='cascade'
    )

    @api.one
    @api.onchange('product_id')
    def product_id_change(self):
        uom_id = False
        product = self.product_id
        if product:
            uom_id = product.uom_id.id
        self.uom_id = uom_id

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
