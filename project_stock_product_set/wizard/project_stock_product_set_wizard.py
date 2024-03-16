# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProjectStockProductSetWizard(models.TransientModel):
    _inherit = "product.set.wizard"
    _name = "project.stock.product.set.wizard"
    _description = "Wizard model to add product set into a task"

    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task",
        required=True,
        default=lambda self: self.env.context.get("active_id")
        if self.env.context.get("active_model") == "project.task"
        else None,
        ondelete="cascade",
    )

    def _compute_product_set_line_ids(self):
        res = super()._compute_product_set_line_ids()
        for rec in self:
            rec.product_set_line_ids = rec.product_set_id.set_line_ids.filtered(
                "product_id"
            )
        return res

    def _prepare_stock_move_lines(self):
        move_lines = []
        for _seq, set_line in enumerate(self._get_lines(), start=1):
            values = set_line._prepare_stock_move_values(self.task_id, self.quantity)
            move_lines.append((0, 0, values))
        return move_lines

    def add_set(self):
        res = super().add_set()
        if not self.task_id:
            return res
        move_lines = self._prepare_stock_move_lines()
        if move_lines:
            self.task_id.write({"move_ids": move_lines})
        return move_lines
