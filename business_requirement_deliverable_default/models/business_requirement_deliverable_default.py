# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessRequirementDeliverable(models.Model):
    _inherit = "business.requirement.deliverable"

    def _prepare_resouce_lines(self):
        rl_data = self.product_id.resource_lines.copy_data()
        rl_data = [(0, 0) + (x,) for x in rl_data]
        return rl_data

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
            self.resource_ids = self._prepare_resouce_lines()
        self.description = description
        self.uom_id = uom_id
        self.unit_price = unit_price


class ProductTemplate(models.Model):
    _inherit = "product.template"

    resource_lines = fields.One2many(
        comodel_name='business.requirement.resource',
        inverse_name='product_template_id',
        string='Business Requirement Resources',
        copy=True,
    )


class BusinessRequirementResource(models.Model):
    _inherit = "business.requirement.resource"

    product_template_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        ondelete='cascade'
    )
