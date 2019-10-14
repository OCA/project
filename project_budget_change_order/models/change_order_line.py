# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ChangeOrderLine(models.Model):
    _name = "project.change_order_line"
    _description = 'Change Order Line'

    note = fields.Text()
    change_order_id = fields.Many2one('project.change_order',
                                      string="Change Order",
                                      required=True)
    budget_line_id = fields.Many2one('crossovered.budget.lines',
                                     string="Budget Line",
                                     required=True)
    change_value = fields.Float(string="Change Value")
    budget_id = fields.Many2one('crossovered.budget', string="Budget")
