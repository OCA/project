# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa
# © 2016 Pedro M. Baeza
# © 2016 Sergio Teruel
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from datetime import datetime


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    date_time = fields.Datetime(default=fields.Datetime.now, string='Date')
    folded = fields.Boolean(related='task_id.stage_id.fold')

    @api.onchange('account_id')
    def onchange_account_id(self):
        if not self.account_id:
            return {'domain': {'task_id': []}}
        self.task_id = False
        project = self.env['project.project'].search(
            [('analytic_account_id', '=', self.account_id.id)], limit=1)
        return {
            'domain': {
                'task_id': [('project_id', '=', project.id),
                            ('stage_id.fold', '=', False)]},
        }

    @api.onchange('task_id')
    def onchange_task_id(self):
        if self.task_id:
            self.account_id = self.task_id.project_id.analytic_account_id.id

    def eval_date(self, vals):
        if 'date_time' in vals and 'date' not in vals:
            vals['date'] = fields.Date.from_string(vals['date_time'])
        return vals

    def create(self, vals):
        return super(AccountAnalyticLine, self).create(self.eval_date(vals))

    def write(self, vals):
        return super(AccountAnalyticLine, self).write(self.eval_date(vals))

    @api.multi
    def button_end_work(self):
        end_date = datetime.now()
        for work in self:
            date = fields.Datetime.from_string(work.date_time)
            work.unit_amount = (end_date - date).total_seconds() / 3600
        return True

    @api.multi
    def button_open_task(self):
        stage = self.env['project.task.type'].search(
            [('fold', '=', False)], limit=1)
        self.mapped('task_id').write({'stage_id': stage.id})

    @api.multi
    def button_close_task(self):
        stage = self.env['project.task.type'].search(
            [('fold', '=', True)], limit=1)
        self.mapped('task_id').write({'stage_id': stage.id})
