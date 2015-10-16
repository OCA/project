# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, _
from openerp.addons.decimal_precision import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.template'

    task_work_ids = fields.One2many(
        comodel_name='product.task.work', inverse_name='product_id',
        string='Task Works')
    task_materials_ids = fields.One2many(
        comodel_name='product.task.materials', inverse_name='product_id',
        string='Materials')

    @api.multi
    def action_compute_price(self):
        wiz = {
            'name': _("Compute Service Price"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'product.price.service.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': '[]',
            'context': {}
                }
        return wiz


class ProductTaskWork(models.Model):
    _name = 'product.task.work'

    product_id = fields.Many2one(
        comodel_name='product.template', string='Product', ondelete='restrict')
    name = fields.Char(string='Name')
    hours = fields.Float(string='Hours')


class ProductTaskMaterials(models.Model):
    _name = 'product.task.materials'

    product_id = fields.Many2one(
        comodel_name='product.template', string='Product', ondelete='restrict')
    material_id = fields.Many2one(
        comodel_name='product.product', string='Material', required=True)
    quantity = fields.Float(
        string='Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'))
