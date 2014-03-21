# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Akretion LDTA (<http://www.akretion.com>).
#
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


class project_functional_block(orm.Model):
    _name = 'project.functional.block'
    _description = 'Functional block to organize projects tasks'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for row in self.read(cr, uid, ids, ['name', 'parent_id'], context=context):
            parent = row['parent_id'] and (row['parent_id'][1]+' / ') or ''
            res.append((row['id'], parent + row['name']))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        return dict(self.name_get(cr, uid, ids, context=context))

    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'sequence': fields.integer('Sequence'),
        'description': fields.text('Description', translate=True),
        'parent_id': fields.many2one(
            'project.functional.block',
            'Parent block'),
        'child_id': fields.one2many(
            'project.functional.block',
            'parent_id',
            'Child block'),
        'complete_name': fields.function(
            _name_get_fnc,
            method=True,
            type='char',
            string='Name'),
        'code': fields.char('Code', size=10),
    }
    _order = 'parent_id, sequence, name'


class project_task(orm.Model):
    _inherit = 'project.task'
    _columns = {
        'functional_block_id': fields.many2one(
            'project.functional.block',
            'Functional Block'),
    }
