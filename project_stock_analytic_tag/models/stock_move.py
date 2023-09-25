# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_analytic_line_from_task(self):
        vals = super()._prepare_analytic_line_from_task()
        task = self.task_id or self.raw_material_task_id
        if task.stock_analytic_tag_ids:
            vals["tag_ids"] = [(6, 0, task.stock_analytic_tag_ids.ids)]
        return vals
