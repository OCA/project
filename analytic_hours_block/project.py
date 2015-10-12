# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Damien Crier
#    Copyright 2014-2015 Camptocamp SA
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

from openerp import models, api, _
from openerp import exceptions


class project_project(models.Model):
    _inherit = 'project.project'

    @api.multi
    def hours_block_tree_view(self):
        self.ensure_one()
        invoice_line_obj = self.env['account.invoice.line']
        hours_block_obj = self.env['account.hours.block']
        domain = [('account_analytic_id', '=', self.analytic_account_id.id)]
        invoice_lines = invoice_line_obj.search(domain)

        invoices = invoice_lines.mapped('invoice_id')
        res_rs = hours_block_obj.search([('invoice_id', 'in', invoices.ids)])
        domain = False
        if res_rs:
            domain = [('id', 'in', res_rs.ids)]
        else:
            raise exceptions.Warning(_('Warning'),
                                     _("No Hours Block for this project"))

        return {
            'name': _('Hours Blocks'),
            'domain': domain,
            'res_model': 'account.hours.block',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'res_id': res_rs.ids,
        }
