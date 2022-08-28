# Copyright 2020-today Commown SCIC (https://commown.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class Project(models.Model):

    _inherit = "project.project"

    net_promoter_score = fields.Integer(
        compute="_compute_net_promoter_score", string="NPS",
        store=True, default=False)

    @api.depends('task_ids.rating_ids.rating')
    def _compute_net_promoter_score(self):
        for record in self:
            task_ids = self.env['project.task'].search([
                ('project_id', '=', record.id),
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
                record.net_promoter_score = False
            else:
                promoters_count = self.env['rating.rating'].search_count(
                    base_domain + [('rating', '>=', 9)])
                detractors_count = self.env['rating.rating'].search_count(
                    base_domain + [('rating', '<=', 6)])
                record.net_promoter_score = int(
                    100 * (1. * promoters_count - detractors_count) / total_count)
