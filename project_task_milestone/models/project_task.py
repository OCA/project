# Copyright 2018 Gontzal Gomez - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    milestone = fields.Boolean(string='Milestone')
    phase_id = fields.Many2one(
        string='Phase', comodel_name='project.task.phase')
    sequence = fields.Integer(string='Sequence')
