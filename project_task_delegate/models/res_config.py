# -*- coding: utf-8 -*-
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProjectConfiguration(models.TransientModel):
    _inherit = 'project.config.settings'

    group_manage_delegation_task = fields.Boolean(
        "Allow task delegation",
        implied_group='project_task_delegate.group_delegate_task',
        help="Allows you to delegate tasks to other users.")
