# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessRequirement(models.Model):
    _inherit = "business.requirement"

    estimated_cost_total = fields.Float(
        compute='_get_estimated_cost_total',
        string='Total Estimated Cost',
        store=True
    )

    @api.one
    @api.depends(
        'draft_estimation_lines.price_total'
    )
    def _get_estimated_cost_total(self):
        cost_total = sum(
            line.price_total for line in self.draft_estimation_lines)
        self.estimated_cost_total = cost_total


class BusinessEstimationLine(models.Model):
    _inherit = "business.estimation.line"

    unit_price = fields.Float(
        string='Unit Price'
    )
    price_total = fields.Float(
        compute='_get_price_total',
        string='Total estimated cost'
    )
    cost_structure_id = fields.Many2one(
        comodel_name='business.requirement.cost.structure',
        string='Cost Structure'
    )

    @api.one
    @api.depends('estimated_time', 'unit_price')
    def _get_price_total(self):
        self.price_total = self.estimated_time * self.unit_price

    @api.one
    @api.onchange('cost_structure_id', 'type_id')
    def cost_structure_id_change(self):
        unit_price = 0
        user_id = False
        structure = self.cost_structure_id
        for line in structure.structure_lines:
            if line.type_id.id == self.type_id.id:
                unit_price = line.unit_price or 0
                user_id = line.user_id.id
        self.unit_price = unit_price
        self.user_id = user_id


class BusinessRequirementCostStructure(models.Model):
    _name = "business.requirement.cost.structure"
    _description = "Business Requirement Cost Structure"

    name = fields.Char('Name', required=True)
    structure_lines = fields.One2many(
        comodel_name='business.requirement.cost.structure.line',
        inverse_name='structure_id',
        string='Business Requirement Cost Structure Lines',
        copy=True,
    )


class BusinessRequirementCostStructureLine(models.Model):
    _name = "business.requirement.cost.structure.line"
    _description = "Business Requirement Cost Structure Line"

    type_id = fields.Many2one(
        comodel_name='business.estimation.type',
        string='Estimation Type',
        ondelete='restrict',
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Default User'
    )
    unit_price = fields.Float(
        string='Unit Price',
        required=True
    )
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='Default UoM'
    )
    structure_id = fields.Many2one(
        comodel_name='business.requirement.cost.structure',
        string='Business Requirement Cost Structure',
        ondelete='cascade'
    )

    @api.one
    @api.onchange('product_id')
    def cost_structure_id_change(self):
        unit_price = 0
        uom_id = False
        product = self.product_id
        if product:
            unit_price = product.list_price or 0
            uom_id = product.uom_id.id
        self.unit_price = unit_price
        self.uom_id = uom_id
