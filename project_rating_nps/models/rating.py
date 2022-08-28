# Copyright 2020-today Commown SCIC (https://commown.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, tools


class Rating(models.Model):
    _inherit = 'rating.rating'

    net_promoter_score = fields.Integer(
        compute="_compute_net_promoter_score", string="NPS", store=True,
        group_operator="avg")

    @api.depends('rating')
    def _compute_net_promoter_score(self):
        for record in self:
            record.net_promoter_score = ((record.rating >= 9 and 100)
                                         or (record.rating <= 6 and -100)
                                         or 0)


class RatingMixin(models.AbstractModel):

    _inherit = 'rating.mixin'

    @api.multi
    def rating_apply(self, rate, token=None, feedback=None, subtype=None):
        """ Overloading of the `rating` module's method to avoid the hard-coded
        path to this module's images.
        """
        Rating, rating = self.env['rating.rating'], None
        if token:
            rating = self.env['rating.rating'].search(
                [('access_token', '=', token)], limit=1)
        else:
            rating = Rating.search([('res_model', '=', self._name),
                                    ('res_id', '=', self.ids[0])], limit=1)
        if rating:
            rating.write(
                {'rating': rate, 'feedback': feedback, 'consumed': True})
            if hasattr(self, 'message_post'):
                feedback = tools.plaintext2html(feedback or '')
                body = ("<img src='/project_rating_nps/static/src"
                        "/img/rate_%d.png' style='width:20px;height:20px;"
                        "float:left;margin-right: 5px;'/>%s")
                # None will set the default author in mail_thread.py
                author_id = rating.partner_id and rating.partner_id.id or None
                self.message_post(
                    body=body % (rate, feedback),
                    subtype=subtype or "mail.mt_comment",
                    author_id=author_id,
                )
            if (hasattr(self, 'stage_id') and self.stage_id
                    and hasattr(self.stage_id, 'auto_validation_kanban_state')
                    and self.stage_id.auto_validation_kanban_state):
                if rating.rating >= 9:
                    self.write({'kanban_state': 'done'})
                if rating.rating <= 6:
                    self.write({'kanban_state': 'blocked'})
        return rating
