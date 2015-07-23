# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   Copyright (C) 2010-2013 Akretion LDTA (<http://www.akretion.com>)
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
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

from openerp import api, fields, models
from datetime import date


class SaleOrder(models.Model):
    _inherit = "sale.order"

    related_project_id = fields.Many2one(
        comodel_name='project.project', string='Project',
        readonly=True, states={'draft': [('readonly', False)]})

    @api.one
    @api.onchange('related_project_id')
    def onchange_related_project_id(self):
        self.project_id = self.related_project_id.analytic_account_id

    def _prepare_project_vals(self):
        name = u" %s - %s - %s" % (
            self.partner_id.name,
            date.today().year,
            self.name)
        return {
            'user_id': self.user_id.id,
            'name': name,
            'partner_id': self.partner_id.id,
        }

    @api.multi
    def action_create_project(self):
        project_obj = self.env['project.project']
        for order in self:
            vals = order._prepare_project_vals()
            project = project_obj.create(vals)
            order.write({
                'related_project_id': project.id,
                'project_id': project.analytic_account_id.id
            })
        return True
