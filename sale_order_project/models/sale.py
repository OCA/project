# -*- coding: utf-8 -*-
# © 2014 Akretion (http://www.akretion.com).
# © 2010-2013 Akretion LDTA (<http://www.akretion.com>)
# © Sébastien BEAU <sebastien.beau@akretion.com>
# © Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from datetime import date


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
            project = project_obj.create(vals)
            order.write({
                'project_id': project.analytic_account_id.id
            })
        return True
