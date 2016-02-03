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

from openerp.osv import orm
from openerp.tools.translate import _

class hr_timesheet_invoice_create(orm.TransientModel):

    _inherit = "hr.timesheet.invoice.create"

    def view_init(self, cr, uid, fields, context=None):
        """
        This function checks for precondition before wizard executes
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param fields: List of fields for default value
        @param context: A standard dictionary for contextual values
        """
        # ts_obj = self.pool['hr.analytic.timesheet']
        # ts_lines = ts_obj.browse(cr, uid, context['active_ids'], context=context)
        aal_obj = self.pool.get(context['active_model'])
        aal_ids = context.get('active_ids', False)
        # aal_ids = [x.line_id.id for x in ts_lines]
        aal_aal = self.pool['account.analytic.line'].browse(cr, uid, aal_ids, context=context)
        for analytic in aal_aal:
            if analytic.invoice_id:
                raise osv.except_osv(_('Warning!'), _("Invoice is already linked to some of the analytic line(s)!"))

    def do_create(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        # Create an invoice based on selected timesheet lines
        invs = self.pool.get(context['active_model']).invoice_cost_create(cr, uid, context['active_ids'], data, context=context)
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        mod_ids = mod_obj.search(cr, uid, [('name', '=', 'action_invoice_tree1')], context=context)[0]
        ################
        res_id = mod_obj.read(cr, uid, mod_ids, ['res_id'], context=context)['res_id']
        act_win = act_obj.read(cr, uid, res_id, [], context=context)
        act_win['domain'] = [('id','in',invs),('type','=','out_invoice')] # invs est none
        act_win['name'] = _('Invoices')
        return act_win