# -*- coding: utf-8 -*-
# Copyright 2017 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class Project(models.Model):
    _inherit = "project.project"

    status_report_ids = fields.One2many(
        'project.status.report',
        'project_id',
        string='Status Reports'
    )
    current_status_id = fields.Many2one(
        'project.status.report',
        string='Current Status',
    )
    current_status_summary = fields.Char(
        related='current_status_id.summary',
    )
    current_status_state = fields.Selection(
        related='current_status_id.state',
    )
