# -*- coding: utf-8 -*-

from openerp import api, fields, models
from datetime import date


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('project_id')
    def _compute_related_project_id(self):
        for rec in self:
            rec.related_project_id = (
                rec.project_id.use_tasks and
                rec.env['project.project'].search(
                    [('analytic_account_id', '=', rec.project_id.id)],
                    limit=1)[:1])

    related_project_id = fields.Many2one(
        comodel_name='project.project', string='Project',
        compute='_compute_related_project_id')

    def _prepare_project_vals(self):
        name = u" %s - %s - %s" % (
            self.today().year,
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
                'project_id': project.analytic_account_id.id
            })
        return True
