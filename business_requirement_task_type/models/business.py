# -*- coding: utf-8 -*-
# © 2015 Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessRequirementCostStructureLine(models.Model):
    _inherit = "business.requirement.cost.structure.line"

    task_type = fields.Many2one(
        comodel_name='business.requirement.task.type',
        string='Deliverable Type',
        ondelete='restrict',
        required=False,
    )


class BusinessRequirementResource(models.Model):
    _inherit = "business.requirement.resource"

    task_type = fields.Many2one(
        comodel_name='business.requirement.task.type',
        string='Task Type',
        ondelete='restrict'
    )

    @api.one
    @api.onchange('cost_structure_id', 'task_type', 'product_id')
    def cost_structure_id_change(self):
        unit_price = 0
        user_id = False
        uom_id = False
        structure = self.cost_structure_id
        for line in structure.structure_lines:
            if line.task_type.id == self.task_type.id and \
                    line.product_id.id == self.product_id.id:
                unit_price = line.unit_price or 0
                user_id = line.user_id.id
                uom_id = line.uom_id.id
        self.unit_price = unit_price
        self.user_id = user_id
        self.uom_id = uom_id


class BusinessRequirementTaskType(models.Model):
    _name = "business.requirement.task.type"
    _description = "Business Requirement Task Type"

    name = fields.Char(string='Name', required=True)
