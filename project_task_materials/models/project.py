# -*- coding: utf-8 -*-
# Copyright 2012 - 2013 Daniel Reis
# Copyright 2015 - Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2016 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class Task(models.Model):
    _inherit = "project.task"

    material_ids = fields.One2many(
        comodel_name='project.task.materials', inverse_name='task_id',
        string='Materials used')


class ProjectTaskMaterials(models.Model):
    _name = "project.task.materials"
    _description = "Task Materials Used"

    task_id = fields.Many2one(
        comodel_name='project.task', string='Task', ondelete='cascade',
        required=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity')

    @api.multi
    @api.constrains('quantity')
    def _check_quantity(self):
        for material in self:
            if not material.quantity > 0.0:
                raise ValidationError(
                    _('Quantity of materials consumed must be greater than 0.')
                )
