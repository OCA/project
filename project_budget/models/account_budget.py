# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    project_id = fields.Many2one('project.project', string="Project")
    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string="Default Analytic Account")
