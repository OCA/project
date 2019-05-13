# Copyright 2019 Patrick Wilson <patrickraymondwilson@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Project(models.Model):
    _inherit = "project.project"
    _inherits = {"account.analytic.account": "analytic_account_id"}

    analytic_account_id = fields.Many2one(
        required=True, ondelete="restrict", index=True
    )
