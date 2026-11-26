# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def reverse_moves(self, is_modify=False):
        action = super().reverse_moves(is_modify)
        project_revenue = self.move_ids.mapped("project_revenue_recognition_id")
        if project_revenue:
            self.new_move_ids.write(
                {"project_revenue_recognition_id": project_revenue.id}
            )
            project_revenue.action_reverse()
        return action
