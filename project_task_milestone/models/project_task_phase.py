# Copyright 2018 Gontzal Gomez - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProjectTaskPhase(models.Model):
    _name = 'project.task.phase'
    _description = 'Phases of Tasks'

    name = fields.Char(string='Name', translate=True, required=True)
