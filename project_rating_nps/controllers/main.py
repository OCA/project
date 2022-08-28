# Copyright 2020-today Commown SCIC (https://commown.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.rating.controllers.main import Rating


class NetPromoterScoreRating(Rating):

    @http.route()
    def open_rating(self, token, rate, **kwargs):
        """ Override rating module's controller

        to allow all NPS rates and set NPS rate names.
        """

        assert rate in set(range(11)), "Incorrect rating"
        rating = request.env['rating.rating'].sudo().search([
            ('access_token', '=', token),
        ])
        if not rating:
            return request.not_found()

        rating.sudo().write({'rating': rate, 'consumed': True})

        rate_name = (rate >= 9 and 'promoter' or rate >= 7 and 'passive'
                     or 'detractor')
        lang = rating.partner_id.lang or 'en_US'
        view_model = request.env['ir.ui.view'].with_context(lang=lang)

        return view_model.render_template(
            'project_rating_nps.rating_external_page_submit', {
                'rating': rating, 'token': token,
                'rate_name': rate_name, 'rate': rate,
            })
