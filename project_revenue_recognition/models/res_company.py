# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    project_revenue_recognition_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Revenue Recognition Journal",
    )
    project_accrued_revenue_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Accrued Revenue Account",
    )
    project_deferred_revenue_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Deferred Revenue Account",
    )
    project_revenue_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Revenue Account",
    )
