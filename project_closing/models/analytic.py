from odoo import models, api


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def toggle_active(self):
        for analytic in self.with_context(
                doing_project_toggle_active=True,
                active_test=False):
            analytic.project_ids.toggle_active()
        return super(AnalyticAccount, self).toggle_active()
