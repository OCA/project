# -*- coding: utf-8 -*-
# © 2014 Akretion - Sébastien BEAU <sebastien.beau@akretion.com>
# © 2014 Akretion - Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import date


class SaleOrder(models.Model):
    _inherit = "sale.order"

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
                'project_id': project.analytic_account_id.id
            })
        return True
