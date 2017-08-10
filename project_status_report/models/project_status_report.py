# -*- coding: utf-8 -*-
# Copyright 2017 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProjectStatusReport(models.Model):
    _name = 'project.status.report'
    _description = 'Status Report'
    _rec_name = 'date'
    _order = 'date desc'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        index=True,
    )
    date = fields.Date(
        'Status Date',
        default=lambda s: fields.Date.context_today(s),
        required=True,
        index=True
    )
    summary = fields.Char()
    description = fields.Html()
    state = fields.Selection(
        [('normal', 'On track, minor issues'),
         ('blocked', 'Off track'),
         ('done', 'On track')],
        'Overall State',
        default='normal',
        copy=False,
    )
    is_current_status = fields.Boolean(
        'Is Current Status?',
        compute='_compute_is_current_status',
    )

    _sql_constraints = [
        ('project_status_report_date_uniq',
         'UNIQUE (project_id, date)',
         'Status Report Date must be unique!'),
    ]

    @api.depends('project_id', 'date')
    def _compute_is_current_status(self):
        for rec in self:
            rec.is_current_status = rec.project_id.current_status_id == rec

    @api.multi
    def _set_project_current_status(self):
        """
        Update the Project's current status report.
        Only do so if a status summary is given.
        """
        for this in self:
            current_status_id = this.project_id.current_status_id
            if this.summary and this.date > current_status_id.date:
                this.project_id.current_status_id = this
        return self

    @api.model
    def create(self, vals):
        new = super(ProjectStatusReport, self).create(vals)
        new._set_project_current_status()
        return new

    @api.multi
    def write(self, vals):
        super(ProjectStatusReport, self).write(vals)
        self._set_project_current_status()
        return True
