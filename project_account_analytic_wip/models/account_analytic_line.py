# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class AnalyticLine(models.Model):
    _name = "account.analytic.line"
    _inherit = ["account.analytic.line"]

    def _timesheet_preprocess(self, vals):
        """
        Add Product and Tracking Item to Timesheet Line
        """
        res = super()._timesheet_preprocess(vals)
        if vals.get("task_id") and vals.get("unit_amount"):
            task = self.env["project.task"].browse(vals["task_id"])
            so_line = task.sale_line_id
            if "product_id" not in vals and so_line.product_id:
                res["product_id"] = so_line.product_id.id
            if "analytic_tracking_item_id" not in vals:
                res["analytic_tracking_item_id"] = so_line.analytic_tracking_item_id.id
        return res
