# Copyright 2026 ForgeFlow S.L.
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_task_prepare_values(self, project):
        res = super()._timesheet_create_task_prepare_values(project)
        if self.order_id.client_order_ref:
            res["customer_reference"] = self.order_id.client_order_ref
        return res
