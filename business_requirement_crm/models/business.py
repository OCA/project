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
        string='Total Revenue from BR'
    )

    @api.one
    def _get_resource_cost_total(self):
        linked_brs = self.project_id and self.project_id.br_ids or []
        self.resource_cost_total = sum(
            [br.resource_cost_total for br in linked_brs
                if br.state not in ('drop', 'cancel')]) or 0

    @api.one
    @api.onchange('project_id')
    def project_id_change(self):
        if self.project_id:
            self.partner_id = self.project_id.partner_id.id
