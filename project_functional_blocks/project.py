# -*- coding: utf-8 -*-
from osv import fields, osv

class project_functional_block(osv.osv):
    _name = 'project.functional_block'
    _description = 'Functional block to organize projects tasks'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for row in self.read(cr, uid, ids, ['name','parent_id'], context=context):
            parent = row['parent_id'] and (row['parent_id'][1]+' / ') or ''
            res.append((row['id'], parent + row['name']))
        return res
        
    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        return dict( self.name_get(cr, uid, ids, context=context) )

    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'description': fields.text('Description', translate=True),
        'parent_id': fields.many2one('project.functional_block', 'Parent block', select=True),
        'child_id': fields.one2many('project.functional_block', 'parent_id', 'Child block'),
        'complete_name': fields.function(_name_get_fnc, method=True, type='char', string='Name'),
        'code': fields.char('Code', size=10),
    }
    _order = 'parent_id,name'

    
project_functional_block()

class project_task(osv.osv):
    _inherit = 'project.task'
    _columns = {
        'functional_block_id': fields.many2one('project.functional_block', 'Functional Block'),
    }
    _constraints = [
        (osv.osv._check_recursion, 'Error! Cannot create recursive cycle.', ['parent_id'])
    ]
    
project_task()
