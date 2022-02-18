# Copyright 2019 Valentin Vinagre <valentin.vinagre@qubiq.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    task_material_id = fields.One2many(
        comodel_name="project.task.material",
        inverse_name="stock_move_id",
        string="Project Task Material",
    )

    def _action_done(self, cancel_backorder=False):
        # The analytical amount is updated with the value of the
        # stock movement, because if the product has a tracking by
        # lot / serial number, the cost when creating the
        # analytical line is not correct.
        res = super()._action_done(cancel_backorder=cancel_backorder)
        self.mapped("task_material_id")._update_unit_amount()
        return res
