# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ChangeOrderStage(models.Model):
    _name = 'project.change_order_stage'
    _order = 'sequence'
    _description = 'Change Order Stage'

    name = fields.Char(string="Stage", required=True)
    sequence = fields.Integer(string="Sequence")
    description = fields.Text(string="Description")
    fold = fields.Boolean(string="Folded")
    is_close = fields.Boolean(string="Closing Kanban Stage")

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code(
            'project.change_order_stage') or 0
        vals['sequence'] = seq
        return super(ChangeOrderStage, self).create(vals)
