# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from osv import fields, osv

class contract_type(osv.osv):

    _name = "contract.type"
    _description = "Contracts"
    _order = "name"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=64, required=True),
        'model_id': fields.many2one('ir.model', 'Model', required=True, readonly=True),
        'active': fields.boolean('Active', help="If the active field is set to False,\
                 it will allow you to hide the contract type without removing it."),
        'contract_ids': fields.one2many('contract.contract', 'type_id', 'Contract list', readonly=True),
        'field_id': fields.many2one('ir.model.fields', 'Fields', readonly=True),
    }
    
    _defaults = {
        'active': lambda *a: True,
    }
    
contract_type()

class contract_category(osv.osv):

    _name = "contract.category"
    _description = "Contracts category"
    _order = "name"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=64, required=True),
    }
    
    _sql_constraints = [
        ('code', 'unique (code)', 'The code must be unique !')
    ]
    
contract_category()

class contract_contract(osv.osv):

    _name = "contract.contract"
    _description = "Contracts"
    _inherits = {'account.analytic.account': "analytic_account_id"}
    
    def _select_objects(self, cr, uid, context=None):
        model_pool = self.pool.get('ir.model')
        ids = model_pool.search(cr, uid, [('name','not ilike','.')])
        res = model_pool.read(cr, uid, ids, ['model', 'name'])
        return [(r['model'], r['name']) for r in res] +  [('','')]
    
    def _get_link(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids):
            res[obj.id] = (obj.obj_id and obj.type_id.model_id and obj.type_id.model_id.model + ',' + str(obj.obj_id)) or False
        return res
    
    def _get_type_id(self, cr, uid, context=None):
        print context
        type_id = False
        if context.get('type_id', False):
            type_id = context.get('type_id', False)
        elif context.get('module', False) and context.get('xml_name', False):
            module = context.get('module', False)
            name = context.get('xml_name', False)
            model_data = self.pool.get('ir.model.data')
            data_ids = model_data.search(cr, uid, [('module', '=', module),('name', '=', name)])
            if data_ids:
                type_id = model_data.browse(cr, uid, data_ids[0]).res_id
        return type_id

    _columns = {
        'ref': fields.char('Reference', size=64),
        'type_id': fields.many2one('contract.type', 'Contract Type', required=True, readonly=True),
        'obj_id': fields.integer('Object ID', readonly=True),
        'active': fields.boolean('Active', help="If the active field is set to False,\
                 it will allow you to hide the contract without removing it."),
        'link': fields.function(_get_link, method=True, string='Link', type='char', selection=_select_objects, size=256, store=True),
        'category_id': fields.many2one('contract.category', 'Contract category'),
        'interval_number': fields.integer('Interval Qty'),
        'interval_type': fields.selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')], 'Interval Unit'),
        'date_init': fields.datetime('First Billing Date'),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic account', required=True, ondelete="cascade"),
    }
    
    _defaults = {
        'active' : lambda *a: True,
        'type_id': lambda self,cr,uid,c: self._get_type_id(cr, uid, c),
        'obj_id': lambda self,cr,uid,c: c.get('obj_id', False),
    }

    def create(self, cr, uid, vals, context=None):
        if 'type_id' in vals and vals['type_id']:
            type = self.pool.get('contract.type').browse(cr, uid, vals['type_id'])
            field_name = type.field_id and type.field_id.name
            vals.update({field_name: vals['obj_id']})
        elif context.get('type_id', False):
            type = self.pool.get('contract.type').browse(cr, uid, context.get('type_id', False))
            field_name = type.field_id and type.field_id.name
            if context.get('obj_id',False):
                vals.update({field_name: context.get('obj_id',False)})
        return super(contract_contract, self).create(cr, uid, vals, context=context)
    
contract_contract()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
