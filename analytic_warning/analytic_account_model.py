# -*- coding: utf-8 -*-
# Copyright 2015 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
from openerp.addons.warning.warning import (WARNING_MESSAGE, WARNING_HELP)


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    project_task_warn = fields.Selection(
        WARNING_MESSAGE, 'Task Warning Type',
        help=WARNING_HELP, required=True, default='no-message')
    project_task_warn_msg = fields.Text('Task Warning Message')
