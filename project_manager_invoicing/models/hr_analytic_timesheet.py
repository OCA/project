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

class hr_timesheet_line(orm.Model):
    _inherit = "hr.analytic.timesheet"

    def action_confirm(self, cr, uid, ids, context=None):
        timesheet_lines = self.browse(cr, uid, ids, context=context)
        aal_ids = [x.line_id.id for x in timesheet_lines]
        self.pool['account.analytic.line'].action_confirm(
            cr, uid, aal_ids, context=context)

    def action_reset_to_draft(self, cr, uid, ids, context=None):
        timesheet_lines = self.browse(cr, uid, ids, context=context)
        aal_ids = [x.line_id.id for x in timesheet_lines]
        self.pool['account.analytic.line'].action_reset_to_draft(
            cr, uid, aal_ids, context=context)

    def invoice_cost_create(self, cr, uid, ids, data=None, context=None):
        timesheet_lines = self.browse(cr, uid, ids, context=context)
        aal_ids = [x.line_id.id for x in timesheet_lines]
        return self.pool['account.analytic.line'].invoice_cost_create(
            cr, uid, aal_ids, data=data, context=context)

    def check_invoiceable_line(self, cr, uid, ids, context=None):
        # check that no timesheet line is in a not-done timesheet,
        # using the account_analytic_line method
        timesheet_lines = self.browse(cr, uid, ids, context=context)
        aal_ids = [x.line_id.id for x in timesheet_lines]
        self.pool['account.analytic.line'].check_invoiceable_line(
            cr, uid, aal_ids, context=context)

    # def _check_line_state(self, cr, uid, ids, context=None):
