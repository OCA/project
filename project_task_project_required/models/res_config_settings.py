# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_project_task_project_required = fields.Boolean(
        string='Require Projects on Tasks',
        related='company_id.is_project_task_project_required',
        readonly=False,
    )
