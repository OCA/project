# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2013 Daniel Reis
#    Copyright (C) 2015 - Antiun Ingeniería S.L. - Sergio Teruel
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields


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
