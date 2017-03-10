# -*- coding: utf-8 -*-
# © 2012 Daniel Reis
# © 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProjectTaskCause(models.Model):
    _name = 'project.task.cause'
    _description = 'Issue Cause'
    _order = 'sequence'

    name = fields.Char(string='Cause', required=True, translate=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    code = fields.Char(string='Code')
