# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from datetime import datetime


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _order = 'date_time desc'

    date_time = fields.Datetime(default=fields.Datetime.now,
                                string='Date time')

    def eval_date(self, vals):
        if vals.get('date_time'):
            vals['date'] = fields.Date.to_date(vals['date_time'])
        return vals

    @api.model
    def create(self, vals):
        return super(AccountAnalyticLine, self).create(self.eval_date(vals))

    @api.multi
    def write(self, vals):
        return super(AccountAnalyticLine, self).write(self.eval_date(vals))

    @api.multi
    def button_end_work(self):
        now = datetime.now()
        for line in self:
            line.unit_amount = (now - line.date_time).total_seconds() / 3600
        return True
