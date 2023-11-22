# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProductSetAddFromTask(models.TransientModel):
    _inherit = "product.set.add"
    _name = "product.set.add.from.task"
    _description = "product.set.add.from.task"

    order_id = fields.Many2one(required=False)
    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task",
        required=True,
        default=lambda self: self.env.context.get("active_id")
        if self.env.context.get("active_model") == "project.task"
        else None,
        ondelete="cascade",
    )

    def _prepare_stock_move_lines(self):
        move_lines = []
        for _seq, set_line in enumerate(self._get_lines(), start=1):
            values = set_line._prepare_stock_move_values(self.task_id, self.quantity)
            move_lines.append((0, 0, values))
        return move_lines

    def add_set(self):
        if not self.task_id:
            return super().add_set()
        self._check_partner()
        move_lines = self._prepare_stock_move_lines()
        if move_lines:
            self.task_id.write({"move_ids": move_lines})
        return move_lines
