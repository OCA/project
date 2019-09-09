# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    budget_id = fields.Many2one('crossovered.budget', string="Budget")
    budget_id_lines = fields.One2many(
        related='budget_id.crossovered_budget_line_ids',
        string="Budget Lines")
    budget_state = fields.Selection(
        related='budget_id.state',
        string="Budget Status")
