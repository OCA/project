# -*- coding: utf-8 -*-
# Copyright (C) 2019  Gabriel Cardoso de Faria - KMEE - www.kmee.com.br
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = [
        'project.task',
        'project.wsjf.mixin',
    ]
    _order = 'wsjf desc, sequence'

    @api.model
    def default_get(self, fields):
        defaults = super(ProjectTask, self).default_get(fields)
        if self.project_id:
            defaults.update({
                'business_value': self.project_id.business_value,
                'time_criticality': self.project_id.time_criticality,
                'risk_reduction': self.project_id.risk_reduction,
                'internal_pressure': self.project_id.internal_pressure,
                'job_size': self.project_id.job_size,
            })
        return defaults
