# -*- coding: utf-8 -*-
# Copyright (C) 2019  Gabriel Cardoso de Faria - KMEE - www.kmee.com.br
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = [
        'project.task',
        'project.wsjf.mixin',
    ]
    _order = 'wsjf desc, sequence'

    @api.onchange('project_id')
    def _onchange_project_id(self):
        for record in self:
            if record.project_id:
                record.write({
                    'business_value': record.project_id.business_value,
                    'time_criticality': record.project_id.time_criticality,
                    'risk_reduction': record.project_id.risk_reduction,
                    'internal_pressure': record.project_id.internal_pressure,
                    'job_size': record.project_id.job_size,
                })
