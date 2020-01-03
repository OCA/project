# -*- coding: utf-8 -*-
# Copyright (C) 2019  Gabriel Cardoso de Faria - KMEE - www.kmee.com.br
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api

FIBONACCI = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (5, '5'),
    (8, '8'),
    (13, '13'),
    (21, '21'),
]


class ProjectWSJFMixin(models.AbstractModel):
    """ Mixin class for WSJF prioritization model
    """

    _name = 'project.wsjf.mixin'
    _description = 'Project WSJF Mixin'

    business_value = fields.Selection(
        string="Business Value",
        selection=FIBONACCI,
        default=1,
    )

    time_criticality = fields.Selection(
        string="Time Criticality",
        selection=FIBONACCI,
        default=1,
    )

    risk_reduction = fields.Selection(
        string="Risk Reduction",
        selection=FIBONACCI,
        default=1,
    )

    internal_pressure = fields.Selection(
        string="Internal Pressure",
        selection=FIBONACCI,
        default=8,
    )

    job_size = fields.Selection(
        string="Job Size",
        selection=FIBONACCI,
        default=1,
    )

    wsjf = fields.Float(
        string="WSJF",
        compute='_compute_wsjf_value',
        store=True,
    )

    @api.depends('business_value', 'time_criticality', 'risk_reduction',
                 'internal_pressure', 'job_size')
    def _compute_wsjf_value(self):
        for record in self:
            record.wsjf = (float(record.business_value) +
                           float(record.time_criticality) +
                           float(record.risk_reduction) +
                           float(record.internal_pressure)
                           ) / float(record.job_size)
