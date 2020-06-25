# Copyright 2019 Onestein
# Copyright 2020 Manuel Calero - Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

PROBABILITY = {
    1: 'Rare',
    2: 'Unlikely',
    3: 'Possible',
    4: 'Likely',
    5: 'Very likely'
}

IMPACT = {
    1: 'Trivial',
    2: 'Minor',
    3: 'Moderate',
    4: 'Significant',
    5: 'Extreme'
}

RATING = {
    1: 'N/A',
    2: 'Trivial',
    3: 'Very Low',
    4: 'Low',
    5: 'Low-Medium',
    6: 'Medium',
    7: 'Medium-High',
    8: 'High',
    9: 'Very High',
    10: 'Critical'
}

PROXIMITY = {
    1: 'Very low',
    2: 'Low',
    3: 'Medium',
    4: 'High',
    5: 'Very High',
    6: 'Imminent'
}


class ProjectRisk(models.Model):
    _inherit = ['mail.thread']
    _name = 'project.risk'
    _description = 'Project Risk'

    project_id = fields.Many2one(
        comodel_name='project.project',
        required=True
    )

    project_risk_category_id = fields.Many2one(
        string='Category',
        comodel_name='project.risk.category',
        required=True,
    )

    name = fields.Char(
        required=1
    )

    description = fields.Html()

    probability = fields.Selection(
        required=True,
        selection=list(PROBABILITY.items()),
        track_visibility='onchange'
    )

    impact = fields.Selection(
        required=True,
        selection=list(IMPACT.items())
    )

    rating = fields.Selection(
        compute='_compute_rating',
        store=True,
        selection=list(RATING.items())
    )

    proximity = fields.Selection(
        selection=list(PROXIMITY.items()),
        track_visibility='onchange'
    )

    project_risk_response_category_id = fields.Many2one(
        comodel_name='project.risk.response.category',
        string='Response Category'
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('closed', 'Closed')
        ],
        default='draft',
        track_visibility='onchange'
    )

    owner_id = fields.Many2one(
        string='Owner',
        comodel_name='res.users',
        track_visibility='onchange'
    )

    actionee_id = fields.Many2one(
        string='Actionee',
        comodel_name='res.users',
        track_visibility='onchange'
    )

    project_risk_response_ids = fields.One2many(
        string='Response',
        comodel_name='project.risk.response',
        inverse_name='project_risk_id'
    )

    @api.depends('probability', 'impact')
    def _compute_rating(self):
        for risk in self:
            risk.rating = risk.probability + risk.impact
