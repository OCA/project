# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa
# © 2016 Pedro M. Baeza
# © 2016 Sergio Teruel
# © 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from datetime import datetime


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    date_time = fields.Datetime(default=fields.Datetime.now, string='Date')
    folded = fields.Boolean(string='Folded', compute='_compute_folded')

    @api.depends('task_id.stage_id.fold')
    def _compute_folded(self):
        for rec_analytic in self:
            rec_analytic.folded = rec_analytic.task_id.stage_id.fold

    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.task_id.project_id.analytic_account_id != self.account_id:
            self.task_id = False
        domain = {'task_id': []}
        if self.account_id:
            project = self.env['project.project'].search(
                [('analytic_account_id', '=', self.account_id.id)], limit=1)
            domain = {'task_id': [('project_id', '=', project.id),
                                  ('stage_id.fold', '=', False)]}
        return {'domain': domain}

    @api.onchange('task_id')
    def onchange_task_id(self):
        if self.task_id:
            self.account_id = self.task_id.project_id.analytic_account_id.id

    def eval_date(self, vals):
        if 'date_time' in vals and 'date' not in vals:
            vals['date'] = fields.Date.from_string(vals['date_time'])
        return vals

    @api.model
    def create(self, vals):
        return super(AccountAnalyticLine, self).create(self.eval_date(vals))

    @api.multi
    def write(self, vals):
        return super(AccountAnalyticLine, self).write(self.eval_date(vals))

    @api.multi
    def button_end_work(self):
        end_date = datetime.now()
        for line in self:
            date = fields.Datetime.from_string(line.date_time)
            line.unit_amount = (end_date - date).total_seconds() / 3600
        return True

    @api.multi
    def button_open_task(self):
        for line in self.filtered('task_id'):
            if line.task_id.project_id:
                stage = self.env['project.task.type'].search(
                    [('project_ids', '=', line.task_id.project_id.id),
                     ('fold', '=', False)], limit=1)
                line.task_id.write({'stage_id': stage.id})

    @api.multi
    def button_close_task(self):
        for line in self.filtered('task_id'):
            if line.task_id.project_id:
                stage = self.env['project.task.type'].search(
                    [('project_ids', '=', line.task_id.project_id.id),
                     ('fold', '=', True)], limit=1)
                line.task_id.write({'stage_id': stage.id})
