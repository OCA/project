# -*- coding: utf-8 -*-
# © 2016 Didotech srl (http://www.didotech.com)
# © Andrei Levin <andrei.levin@didotech.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProjectOrderSelect(models.TransientModel):
    _name = 'project.order.select'

    sale_order_id = fields.Many2one('sale.order', string='Sale Orders')
    project_id = fields.Many2one('project.project', string='Projects')
    partner_id = fields.Many2one('res.partner', string='Client')

    @api.multi
    def action_connect_sale_order(self):
        self.sale_order_id.project_id = self.project_id.analytic_account_id.id
        return {'type': 'ir.actions.act_window_close'}
