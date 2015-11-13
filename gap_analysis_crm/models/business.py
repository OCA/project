# -*- coding: utf-8 -*-
# © <YEAR(2015)>
# <AUTHOR(Elico Corp, contributor: Eric Caudal, Alex Duan, Xie XiaoPeng)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BusinessRequirement(models.Model):
    _inherit = "business.requirement"

    lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Opportunity'
    )


class CrmLead(models.Model):
    _inherit = "crm.lead"

    br_ids = fields.One2many(
        comodel_name='business.requirement',
        inverse_name='lead_id',
        string='Business Analysis',
        copy=False
    )
    estimated_time_total = fields.Float(
        compute='_get_estimated_time_total',
        string='Total Estimated Time',
    )
    estimated_cost_total = fields.Float(
        compute='_get_estimated_cost_total',
        string='Total Estimated Cost',
    )

    @api.one
    def _get_estimated_time_total(self):
        time_total = 0
        for br in self.br_ids:
            if br.drop or br.state in ('cancel'):
                continue
            time_total += br.estimated_time_total
        self.estimated_time_total = time_total

    @api.one
    def _get_estimated_cost_total(self):
        cost_total = 0
        for br in self.br_ids:
            if br.drop or br.state in ('cancel'):
                continue
            cost_total += br.estimated_cost_total
        self.estimated_cost_total = cost_total
