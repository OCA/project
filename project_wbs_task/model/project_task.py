# Copyright 2018 ForgeFlow S.L.
# Copyright 2015 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Task(models.Model):
    _inherit = 'project.task'

    analytic_account_id = fields.Many2one(
        related='project_id.analytic_account_id',
        relation='account.analytic.account',
        string='Project Analytic Account', store=True, readonly=True,
        copy=False
    )
    project_complete_wbs_code = fields.Char(
        'Full WBS Code',
        related='analytic_account_id.complete_wbs_code',
        readonly=True
    )
    project_complete_wbs_name = fields.Char(
        'Full WBS Name',
        related='analytic_account_id.complete_wbs_name',
        readonly=True
    )
