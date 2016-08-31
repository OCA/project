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


class ProjectOrderSelect(models.TransientModel):
    _name = 'project.order.select'

    sale_order_id = fields.Many2one('sale.order', string=_('Sale Orders'))
    project_id = fields.Many2one('project.project', string=_('Projects'))
    partner_id = fields.Many2one('res.partner', string=_('Client'))

    @api.multi
    def action_connect_sale_order(self):
        self.sale_order_id.project_id = self.project_id.analytic_account_id.id
        return {'type': 'ir.actions.act_window_close'}
