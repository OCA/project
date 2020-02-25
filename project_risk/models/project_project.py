# Copyright 2019 Onestein
# Copyright 2020 Manuel Calero - Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Project(models.Model):
    _inherit = 'project.project'

    project_risk_ids = fields.One2many(
        comodel_name='project.risk',
        inverse_name='project_id'
    )

    project_risk_count = fields.Integer(
        compute='_compute_risk_count'
    )

    def _compute_risk_count(self):
        for project in self:
            project.project_risk_count = len(project.project_risk_ids)

    def view_risk(self):
        self.ensure_one()
        action = self.env.ref('project_risk.project_risk_action')
        action = action.read()[0]
        action['context'] = {
            'default_project_id': self.id
        }
        action['domain'] = [
            ('project_id', '=', self.id)
        ]
        return action
