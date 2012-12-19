# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Daniel Reis
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

class crm_case_categ(orm.Model):
    _inherit = "crm.case.categ"
    _order   = 'parent_id, name' 
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        for row in self.read(cr, uid, ids, ['name','parent_id'], context=context):
            parent = row['parent_id'] and (row['parent_id'][1]+' / ') or ''
            res.append((row['id'], parent + row['name']))
        return res
        
    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'parent_id': fields.many2one('crm.case.categ', 'Parent'),
        'child_ids': fields.many2many('crm.case.categ', 'crm_case_categ_parent_rel', 'parent_id', 'categ_id', 'Child Categories'),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
        'code': fields.char('Code', size=10),
    }
    _constraints = [
        (orm.Model._check_recursion, 'Error! Cannot create recursive cycle.', ['parent_id'])
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


