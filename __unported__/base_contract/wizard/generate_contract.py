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

class generate_contract_type(osv.osv_memory):
    
    _name = "generate.contract.type"
    _description = "Contract Type Generator"
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=64, required=True),
        'model_id': fields.many2one('ir.model', 'Model', required=True),
    }
    
    def on_change_model_id(self, cr, uid, id, model_id, context=None):
        if context is None:
            context = {}
        if not model_id:
            return {}
        name = self.pool.get('ir.model').browse(cr, uid, model_id).name
        contract_type = 'Contract ' + name
        return {'value': {'name': contract_type, 'code': contract_type.replace(' ','_').lower()}}
    
    def generate_type(self, cr, uid, ids, context):
        if not context:
            context = {}
        obj_ids = self.browse(cr, uid, ids, context)
        type_obj = self.pool.get('contract.type')
        act_obj = self.pool.get('ir.actions.act_window')
        mod_obj = self.pool.get('ir.model.data')
        model_obj = self.pool.get('ir.model')
        
        for obj in obj_ids:
            name = obj.name
            code = obj.code
            model_id = obj.model_id
            
            data_field = {
                    'model': 'contract.contract',
                    'relation': model_id.model,
                    'model_id': model_obj.search(cr, uid, [('model', '=', 'contract.contract')])[0],
                    'name': 'x_contract_' + code,
                    'field_description': model_id.name,
                    'state': 'manual',
                    'ttype': 'many2one',
                    'selection': False,
                    'on_delete': 'set null',
                    }
            
            field_id = self.pool.get('ir.model.fields').create(cr, 1, data_field)
            
            create_id = type_obj.create(cr, uid, {
                                                  'name': name,
                                                  'code': code,
                                                  'model_id': model_id.id,
                                                  'field_id': field_id,
                                                  }, context)
            data_field_o2m = {
                    'model': model_id.model,
                    'relation': 'contract.contract',
                    'relation_field': 'x_contract_' + code,
                    'model_id': model_id.id,
                    'name': 'x_o2m_contract_' + code,
                    'field_description': name,
                    'state': 'manual',
                    'ttype': 'one2many',
                    'selection': False,
                    'on_delete': 'set null',
                    'domain': False,
                    }
            field_o2m_id = self.pool.get('ir.model.fields').create(cr, 1, data_field_o2m)
            
            domain = "[('obj_id', '=', active_id), ('type_id', '=', %s)]" %(create_id)
            action_id = act_obj.create(cr, uid, {
                                        'name': name,
                                        'type': 'ir.actions.act_window',
                                        'src_model': model_id.model,
                                        'res_model': 'contract.contract',
                                        'view_mode': 'tree,form',
                                        'view_type': 'form',
                                        'target': 'current',
                                        'context': "{'obj_id': active_id, 'type_id':%s}" %(create_id),
                                        'domain': domain,
                                        }, context)
            
            self.pool.get('ir.values').create(cr, uid, {
                                        'name': 'act_' + code,
                                        'key': 'action',
                                        'key2': 'client_action_relate',
                                        'model': model_id.model,
                                        'value': 'ir.actions.act_window,' + str(action_id),
                                        'object': True,
                                        })
        return {'type': 'ir.actions.act_window_close'}
    
generate_contract_type()

class generate_contract(osv.osv_memory):
    
    _name = "generate.contract"
    _description = "Contract Generator"
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'ref': fields.char('Reference', size=64),
        'type_id': fields.many2one('contract.type', 'Contract Type', required=True),
        'obj_id': fields.integer('Object ID', required=True),
        'date_start': fields.date('Begin Date'),
        'date_end': fields.date('End Date'),
        'note': fields.text('Notes'),
        'company_id': fields.many2one('res.company', 'Company'),
    }
    
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
        'type_id': lambda self,cr,uid,c: c.get('type_id', False),
        'obj_id': lambda self,cr,uid,c: c.get('obj_id',False),
    }
    
    def generate_contract(self, cr, uid, ids, context):
        if not context:
            context = {}
        obj_ids = self.browse(cr, uid, ids, context)
        contract_obj = self.pool.get('contract.contract')
        act_obj = self.pool.get('ir.actions.act_window')
        mod_obj = self.pool.get('ir.model.data')
        
        for obj in obj_ids:
            vals = {
                'name': obj.name,
                'type_id': obj.type_id.id,
                'obj_id': obj.obj_id,
                'date_start': obj.date_start,
                'date_end': obj.date_end,
                'notes': obj.note,
                'company_id': obj.company_id and obj.company_id.id or False
            }
            contract_obj.create(cr, uid, vals, context)
        return {'type': 'ir.actions.act_window_close'}
    
generate_contract()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

