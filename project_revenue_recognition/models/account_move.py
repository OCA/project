# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    project_revenue_recognition_id = fields.Many2one(
        comodel_name="project.revenue.recognition",
        copy=False,
    )

    def button_cancel(self):
        res = super().button_cancel()
        recognitions = (
            self.filtered("project_revenue_recognition_id")
            .mapped("project_revenue_recognition_id")
            .filtered(lambda r: r.state == "done")
        )
        if recognitions:
            recognitions.write({"state": "confirm"})
        return res
