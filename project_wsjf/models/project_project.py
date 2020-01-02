# -*- coding: utf-8 -*-
# Copyright (C) 2019  Gabriel Cardoso de Faria - KMEE - www.kmee.com.br
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api


class ProjectProject(models.Model):
    _name = 'project.project'
    _inherit = [
        'project.project',
        'project.wsjf.mixin',
    ]
    _order = 'wsjf desc, sequence'

    internal_pressure = fields.Selection(
        inverse='_inverse_internal_pressure'
    )

    @api.multi
    def _inverse_internal_pressure(self):
        for record in self:
            for task in record.task_ids:
                task.internal_pressure = record.internal_pressure
