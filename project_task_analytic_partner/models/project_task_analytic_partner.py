# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class TaskWork(models.Model):
    _inherit = 'project.task.work'

    to_invoice = fields.Many2one(
        comodel_name='hr_timesheet_invoice.factor',
        string='Invoiceable')
    other_partner_id = fields.Many2one(
        comodel_name='res.partner', string="Other Partner",
        domain="['|', ('parent_id', '=', False), ('is_company', '=', True)]")

    @api.multi
    def update_timesheet_vals(self, vals):
        timesheet_vals = {}
        if 'to_invoice' in vals:
            timesheet_vals['to_invoice'] = vals['to_invoice']
        if 'other_partner_id' in vals:
            timesheet_vals['other_partner_id'] = vals['other_partner_id']
        if timesheet_vals:
            self.hr_analytic_timesheet_id.write(timesheet_vals)

    @api.model
    def create(self, vals):
        res = super(TaskWork, self).create(vals)
        res.update_timesheet_vals(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(TaskWork, self).write(vals)
        self.update_timesheet_vals(vals)
        return res
