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
import logging
_logger = logging.getLogger(__name__)


class project_issue(orm.Model):
    _inherit = 'project.issue'
    _columns = {
        'ref': fields.char('Reference', size=10, readonly=True, select=True, help="Issue sequence number"),
    }

    def create(self, cr, uid, vals, context={}):
        #Compatible with crm_categ_hierarchy
        def get_categ_sequence_id(categ_res):
            return categ_res.sequence_id.id or (
                     hasattr(categ_res, 'parent_id')
                     and categ_res.parent_id
                     and get_categ_sequence_id(categ_res.parent_id)
                   )
        
        ret = super(project_issue, self).create(cr, uid, vals, context=context)
        obj = self.browse(cr, uid, ret, context=context)
        if obj.ref:
            _logger.warn('Found a conflicting sequence assignment. Please check customizations made to Project Issues.')
            return res
        seq_id = get_categ_sequence_id(obj.categ_id)
        if seq_id :
            seq_ret = self.pool.get('ir.sequence').next_by_id(cr, uid, seq_id , context=context)
        else:
            #Default sequence, code 'project.issue'
            seq_ret = self.pool.get('ir.sequence').next_by_code(cr, uid, 'project.issue', context=context)
        self.write(cr, uid, [ret], {'ref': seq_ret}, context=context)
        return ret

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


