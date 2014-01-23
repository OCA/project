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

class contract_contract(osv.osv):

    _inherit = "contract.contract"

    def create(self, cr, uid, vals, context=None):
        contact_type_obj = self.pool.get('contract.type')
        xml = {}
        type_id = False
        if context == None:
            context = {}
        if vals.get('type_id'):
            xml = contact_type_obj._get_xml_ids(cr, uid, [vals.get('type_id')])
            type_id = vals.get('type_id')
        elif context.get('type_id'):
            xml = contact_type_obj._get_xml_ids(cr, uid, [context.get('type_id')])
            type_id = context.get('type_id')
        if xml.get(context.get('type_id')) and xml.get(context.get('type_id'))[0] == 'res_partner_contract.type_partner_contract':
            vals['partner_id'] = vals.get('obj_id', False) or context.get('obj_id', False)
        elif context.get('module') and context.get('module')=='res_partner_contract' and context.get('xml_name') and context.get('xml_name')=='type_partner_contract':
            vals['partner_id'] = vals.get('obj_id', False) or context.get('obj_id', False)
        return super(contract_contract, self).create(cr, uid, vals, context=context)
    
contract_contract()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
