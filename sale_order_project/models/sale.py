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
from datetime import date, datetime
import time


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.one
    @api.depends('project_id')
    def _compute_related_project_id(self):
        self.related_project_id = (
            self.project_id.use_tasks and
            self.env['project.project'].search(
                [('analytic_account_id', '=', self.project_id.id)],
                limit=1)[:1])

    related_project_id = fields.Many2one(
        comodel_name='project.project', string='Project',
        compute='_compute_related_project_id')

    project_template_id = fields.Many2one(
        comodel_name='project.project', string='Project Template',
        domain="[('state','=','template')]",
    )

    @api.model
    def _prepare_project_vals(self, order):
        name = u" %s - %s - %s" % (
            order.partner_id.name,
            date.today().year,
            order.name)
        return {
            'user_id': order.user_id.id,
            'name': name,
            'partner_id': order.partner_id.id,
        }

    @api.multi
    def action_create_project(self):
        project_obj = self.env['project.project']
        for order in self:
            vals = self._prepare_project_vals(order)
            if order.project_template_id:
                new_date_start = fields.Date.context_today(self)
                new_date_end = False
                if order.project_template_id.date_start and \
                        order.project_template_id.date:
                    start_date = date(*time.strptime(
                            order.project_template_id.date_start, '%Y-%m-%d'
                        )[:3])
                    end_date = date(*time.strptime(
                            order.project_template_id.date,
                            '%Y-%m-%d')[:3])
                    new_date_end = (datetime(*time.strptime(
                            new_date_start,
                            '%Y-%m-%d'
                        )[:3])+(end_date-start_date)).strftime('%Y-%m-%d')
                vals.update({
                        'state': 'open',
                        'date_start': new_date_start,
                        'date': new_date_end,
                        'parent_id': order.project_template_id.parent_id.id
                    })
                new_id = order.project_template_id.copy(default=vals)
                order.write({
                    'project_id': new_id.analytic_account_id.id
                })
            else:
                project = project_obj.create(vals)
                order.write({
                    'project_id': project.analytic_account_id.id
                })
                return True
