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

    # WORKING
    def view_init(self, cr, uid, fields, context=None):
        """
        OVERWRITE: now it works with both: hr.analytic.timesheet & account.
        analytic.line
        This function checks for precondition before wizard executes
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param fields: List of fields for default value
        @param context: A standard dictionary for contextual values
        """
        # Modification: get active_model & active__ids
        aal_obj = self.pool.get(context['active_model'])
        aal_ids = context.get('active_ids', False)
        aal_to_inv = aal_obj.browse(cr, uid, aal_ids, context=context)
        for analytic in aal_to_inv:
            if analytic.invoice_id:
                raise orm.except_orm(_('Warning!'), _("Invoice is already \
                    linked to some of the analytic line(s)!"))
            if analytic.state == 'draft':
                raise orm.except_orm(_('Warning!'), _("Invoice in draft state \
                    cannot be invoiced"))

    def do_create(self, cr, uid, ids, context=None):
        """ OVERWRITE: now it works with both: hr.analytic.timesheet & account.
        analytic.line
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        # Create an invoice based on selected timesheet lines
        # Modification => get active_model
        invs = self.pool.get(context['active_model']).invoice_cost_create(
            cr, uid, context['active_ids'], data, context=context)
        mod_obj = self.pool['ir.model.data']
        act_obj = self.pool['ir.actions.act_window']
        mod_ids = mod_obj.search(
            cr,
            uid,
            [('name', '=', 'action_invoice_tree1')],
            context=context)[0]
        ################
        res_id = mod_obj.read(
            cr, uid, mod_ids, ['res_id'], context=context)['res_id']
        act_win = act_obj.read(cr, uid, res_id, [], context=context)
        act_win['domain'] = [('id', 'in', invs),
                             ('type', '=', 'out_invoice')]  # invs est none
        act_win['name'] = _('Invoices')
        return act_win
