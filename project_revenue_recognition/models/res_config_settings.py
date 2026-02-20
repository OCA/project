# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    project_revenue_recognition_journal_id = fields.Many2one(
        comodel_name="account.journal",
        related="company_id.project_revenue_recognition_journal_id",
        readonly=False,
    )
    project_accrued_revenue_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.project_accrued_revenue_account_id",
        readonly=False,
    )
    project_deferred_revenue_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.project_deferred_revenue_account_id",
        readonly=False,
    )
    project_revenue_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.project_revenue_account_id",
        readonly=False,
    )
