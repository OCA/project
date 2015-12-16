# -*- coding: utf-8 -*-
# © 2015 Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessRequirementResource(models.Model):
    _inherit = "business.requirement.resource"

    cost_structure_id = fields.Many2one(
        comodel_name='business.requirement.cost.structure',
        string='Cost Structure'
    )

    @api.one
    @api.onchange('cost_structure_id', 'product_id')
    def cost_structure_id_change(self):
        unit_price = 0
        user_id = False
        uom_id = False
        structure = self.cost_structure_id
        for line in structure.structure_lines:
            if line.product_id.id == self.product_id.id:
                unit_price = line.unit_price or 0
                user_id = line.user_id.id
                uom_id = line.uom_id.id
        self.unit_price = unit_price
        self.user_id = user_id
        self.uom_id = uom_id


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
