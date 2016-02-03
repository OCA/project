# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Denis Leemann
#    Copyright 2016 Camptocamp SA
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
from openerp.osv import orm, fields

# ### TEST modification réalisée dans specific_fnc
# class AssociateInvoice(orm.TransientModel):
#     _inherit = 'associate.aal.to.invoice'

#     def associate_aal(self, cr, uid, ids, context=None):
#     	import pdb; pdb.set_trace();
#         if context is None:
#             context = {}
#         ts_obj = self.pool.get(context['active_model'])
#         ts_ids = context.get('active_ids', False)
#         if isinstance(ids, list):
#             req_id = ids[0]
#         else:
#             req_id = ids
#         current = self.browse(cr, uid, req_id, context=context)
#         aal_obj = self.pool.get('account.analytic.line')
#         aal_obj._check_valid(cr, uid, ids)
#         ts_obj.write(cr, uid, ts_ids,
#                       {'invoice_id': current.invoice_id.id},
#                       context=context)
#         return {
#             'domain': "[('id','in', [%s])]" % (current.invoice_id.id,),
#             'name': 'Associated invoice',
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'account.invoice',
#             'view_id': False,
#             'context': context,
#             'type': 'ir.actions.act_window',
#         }
