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

from tools.translate import _
from osv import fields, osv
from datetime import datetime
import netsvc

class project_functional_block(osv.osv):
    _name = 'project.functional_block'
    _description = 'Functional block to organize projects tasks'
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'parent_id': fields.many2one('project.functional_block', 'Parent block', select=True),
        'child_id': fields.one2many('project.functional_block', 'parent_id', 'Child block'),
        'category_description': fields.text('Block description'),
                }
    _order = 'name asc'
    
project_functional_block()

class project_task(osv.osv):
    _inherit = 'project.task'
    _columns = {
        'functional_block_id': fields.many2one('project.functional_block', 'Functional Block'),
                }
    
project_task()
