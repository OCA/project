# -*- coding: utf-8 -*-
# Copyright (C) 2013,2017 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'
    use_analytic_account = fields.Selection(
        [('no', 'No'), ('yes', 'Optional'), ('req', 'Required')],
        'Use Analytic Account',
        default='no')
