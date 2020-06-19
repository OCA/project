# Copyright 2020 Commown SCIC SAS (https://commown.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Rating(models.Model):
    _inherit = 'rating.rating'

    net_promoter_score = fields.Integer(
        compute="_compute_net_promoter_score", string="NPS", store=True,
        group_operator="avg")

    @api.one
    @api.depends('rating')
    def _compute_net_promoter_score(self):
        self.net_promoter_score = ((self.rating >= 9 and 100)
                                   or (self.rating <= 6 and -100)
                                   or 0)
