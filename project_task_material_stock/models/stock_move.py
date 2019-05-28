# Copyright 2019 Valentin Vinagre <valentin.vinagre@qubiq.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    task_material_id = fields.One2many(
        'project.task.material',
        'stock_move_id',
        string='Project Task Material',
    )

    @api.multi
    def _action_done(self):
        # The analytical amount is updated with the value of the
        # stock movement, because if the product has a tracking by
        # lot / serial number, the cost when creating the
        # analytical line is not correct.
        res = super(StockMove, self)._action_done()
        self.mapped('task_material_id')._update_unit_amount()
        return res
