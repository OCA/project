# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for Odoo
#   Copyright (C) 2016 Didotech srl (http://www.didotech.com).
#   @author Andrei Levin <andrei.levin@didotech.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import api, fields, models, _


class Project(models.Model):
    _inherit = 'project.project'

    sale_order_ids = fields.One2many(
        related='analytic_account_id.sale_order_ids',
        string='Sale Orders',
        readonly=True
    )

    @api.multi
    def action_connect_sale_order(self):
        # launch a wizard to select a Sale Order from existing Orders

        view = self.env['ir.model.data'].get_object_reference(
            'sale_order_project',
            'view_project_sale_order_select_form'
        )
        view_id = view and view[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Customer Invoices'),
            'res_model': 'project.order.select',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'target': 'new',
            'res_id': False,
            'context': {
                'default_project_id': self.id,
                'default_partner_id': self.partner_id.id
            }
        }
