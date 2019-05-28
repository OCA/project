# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProjectPhase(models.Model):
    _name = 'project.phase'
    _description = 'Project Phase'
    _order = 'sequence,name'

    name = fields.Char(string='Name', require=True, translate=True)
    sequence = fields.Integer(string='Sequence')
