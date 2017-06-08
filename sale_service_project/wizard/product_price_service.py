# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class ProductPriceServiceWizard(models.TransientModel):
    _name = 'product.price.service.wizard'

    product_id = fields.Many2one(
        comodel_name='product.product', string='Product')
    uom_id = fields.Many2one('product.uom', string='Unit of measure')

    def _compute_price(self, product, product_service):
        total_hours = sum(product.mapped('task_work_ids.hours') or [0.0])
        total_price_hours = product_service.list_price * total_hours
        materials = product.mapped('task_materials_ids')
        total_price_materials = sum(
            [m.quantity * m.material_id.lst_price for m in materials])
        total_price = total_price_hours + total_price_materials
        return total_price

    @api.multi
    def action_compute_price(self):
        product = self.env['product.template'].browse(
            self._context['active_id'])
        product.write(
            {'list_price': self._compute_price(product, self.product_id)})
