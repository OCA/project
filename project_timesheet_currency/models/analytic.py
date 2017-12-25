# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def _timesheet_postprocess(self, values):
        res = super(AccountAnalyticLine, self)._timesheet_postprocess(values)
        project_id = res.get('project_id')
        amount = res.get('amount') or self.amount

        if project_id and amount:
            project_model = self.env['project.project']
            project = project_model.browse(project_id)
            currency = project.currency_id
            base_currency = self.env.user.company_id.currency_id
            res['timesheet_currency_id'] = base_currency.id
            res['amount'] = currency.with_context(
                date=values['date']).compute(amount, base_currency)
            self.write({
                'timesheet_currency_id': res['timesheet_currency_id'],
                'amount': res['amount'],
            })
        return res

    amount_currency = fields.Float(compute="_get_amount_currency", store=True)
    timesheet_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='TS original currency')

    @api.depends('move_id', 'amount')
    def _get_amount_currency(self):
        for aal in self:
            if aal.move_id:
                aal.amount_currency = aal.move_id.amount_currency
            else:
                aal.amount_currency = (
                    aal.timesheet_currency_id.with_context(
                        date=aal.date).compute(
                            aal.amount,
                            aal.account_id.currency_id))
