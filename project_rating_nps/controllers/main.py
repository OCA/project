# Copyright 2020 Commown SCIC SAS (https://commown.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.rating.controllers.main import Rating


class NetPromoterScoreRating(Rating):

    @http.route()
    def open_rating(self, token, rate, **kwargs):
        rating = request.env['rating.rating'].sudo().search([
            ('access_token', '=', token),
        ])
        if not rating:
            return request.not_found()
        rating.sudo().write({'rating': rate, 'consumed': True})
        rate_name = (rate >= 9 and 'promoter' or rate >= 7 and 'passive'
                     or 'detractor')
        return request.render(
            'project_rating_nps.rating_external_page_submit', {
                'rating': rating, 'token': token,
                'rate_name': rate_name, 'rate': rate,
            })
