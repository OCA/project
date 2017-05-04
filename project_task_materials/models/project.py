# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


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
