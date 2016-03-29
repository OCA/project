# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessRequirementDeliverable(models.Model):
    _inherit = "business.requirement.deliverable"

    def _prepare_resource_lines(self):
        rl_data = self.product_id.sudo().resource_lines.copy_data()
        rl_data = [(0, 0, item) for index, item in enumerate(rl_data)]
        return rl_data

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        super(BusinessRequirementDeliverable, self).product_id_change()
        product = self.product_id
        if product:
            self.resource_ids = self._prepare_resource_lines()


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
        ondelete='set null',
        copy=False
    )
    business_requirement_deliverable_id = fields.Many2one(
        comodel_name='business.requirement.deliverable',
        copy=False
    )
