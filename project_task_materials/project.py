# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2013 Daniel Reis
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

from openerp.osv import fields, orm


class task(orm.Model):
    _inherit = "project.task"
    _columns = {
        'material_ids': fields.one2many(
            'project.task.materials', 'task_id', 'Materials used'),
    }


class project_task_materials(orm.Model):
    _name = "project.task.materials"
    _description = "Task Materials Used"
    _columns = {
        'task_id': fields.many2one(
            'project.task', 'Task', ondelete='cascade', required=True),
        'product_id': fields.many2one(
            'product.product', 'Product', required=True),
        'quantity': fields.float('Quantity'),
        }
