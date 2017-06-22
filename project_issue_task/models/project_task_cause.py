# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectTaskCause(models.Model):
    _name = 'project.task.cause'
    _description = 'Issue Cause'
    _order = 'sequence'

    name = fields.Char(string='Cause', required=True, translate=True)
    description = fields.Text()
    sequence = fields.Integer(default=10)
    code = fields.Char()
