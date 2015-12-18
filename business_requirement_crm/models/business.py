# -*- coding: utf-8 -*-
from openerp import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        ondelete='set null',
    )
    resource_cost_total = fields.Float(
        compute='_get_resource_cost_total',
        string='Total Revenue from BR',
    )

    @api.one
    def _get_resource_cost_total(self):
        cost_total = 0
        linked_brs = self.project_id and self.project_id.br_ids or []
        for br in linked_brs:
            if br.state in ('drop', 'cancel'):
                continue
            cost_total += br.resource_cost_total
        self.resource_cost_total = cost_total

    @api.one
    @api.onchange('project_id')
    def project_id_change(self):
        self.partner_id = self.project_id and self.project_id.partner_id \
            or False
