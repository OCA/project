# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, fields, models, tools


class Project(models.Model):

    _inherit = "project.project"

    net_promoter_score = fields.Integer(
        compute="_compute_net_promoter_score", string="NPS",
        store=True, default=False)

    @api.one
    @api.depends('task_ids.rating_ids.rating')
    def _compute_net_promoter_score(self):
        task_ids = self.env['project.task'].search([
            ('project_id', '=', self.id),
        ])
        base_domain = [
            ('res_model', '=', task_ids._name),
            ('res_id', 'in', task_ids.ids),
            ('consumed', '=', True),
            ('create_date', '>=', fields.Datetime.to_string(
                fields.datetime.now() - timedelta(days=30))),
        ]
        total_count = self.env['rating.rating'].search_count(base_domain)
        if total_count == 0:
            self.net_promoter_score = False
        else:
            promoters_count = self.env['rating.rating'].search_count(
                base_domain + [('rating', '>=', 9)])
            detractors_count = self.env['rating.rating'].search_count(
                base_domain + [('rating', '<=', 6)])
            self.net_promoter_score = int(
                100 * (1. * promoters_count - detractors_count) / total_count)


class ProjectTask(models.Model):

    _inherit = 'project.task'

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
                body = ("<img src='/rating_project_issue_nps/static/src"
                        "/img/rate_%s.png' style='width:20px;height:20px;"
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
                if rating.rating > 5:
                    self.write({'kanban_state': 'done'})
                if rating.rating < 5:
                    self.write({'kanban_state': 'blocked'})
        return rating
