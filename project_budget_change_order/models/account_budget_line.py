# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    name = fields.Char(compute='_compute_budget_line_name')

    @api.depends('crossovered_budget_id',
                 'general_budget_id',
                 'analytic_account_id')
    def _compute_budget_line_name(self):
        for record in self:
            computed_line_name = record.crossovered_budget_id.name
            if record.general_budget_id:
                computed_line_name += ' - ' + record.general_budget_id.name
            record.name = computed_line_name
