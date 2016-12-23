# -*- coding: utf-8 -*-
# Copyright 2015 - 2013 Daniel Reis
# Copyright 2016 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProjectTaskCause(models.Model):
    _name = 'project.task.cause'
    _description = 'Issue Cause'
    _order = 'sequence'

    name = fields.Char(string='Cause', required=True, translate=True)
    description = fields.Text()
    sequence = fields.Integer(default=10)
    code = fields.Char()
