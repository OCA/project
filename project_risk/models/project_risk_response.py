# Copyright 2019 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ProjectRiskResponse(models.Model):
    _name = 'project.risk.response'

    project_risk_id = fields.Many2one(
        comodel_name='project.risk.response'
    )

    sequence = fields.Integer()

    description = fields.Char()
