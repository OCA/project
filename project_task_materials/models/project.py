# -*- coding: utf-8 -*-
# © 2012 - 2013 Daniel Reis
# © 2015 - Antiun Ingeniería S.L. - Sergio Teruel
# © 2017 - Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _


class Task(models.Model):
    _inherit = "project.task"
    
    material_ids = fields.One2many(comodel_name='project.task.materials', 
                                   inverse_name='task_id',
                                   string='Materials used')


class ProjectTaskMaterials(models.Model):
    _name = "project.task.materials"
    _description = "Task Materials Used"

    task_id = fields.Many2one(comodel_name='project.task', required=True,
                              string='Task', ondelete='cascade')
    product_id = fields.Many2one(comodel_name='product.product', 
                                 string='Product', required=True)
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('product.uom', string='Unit of Measure')
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.uom_id = self.product_id.uom_id
        