# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectProject(models.Model):

    _inherit = 'project.project'

    planned_hours = fields.Float(
        string="Planned hours",
        compute='_compute_planned_hours',
        store=True
    )
    total_hours_spent = fields.Float(
        string="Total hours spent",
        compute='_compute_spent_hours',
        store=True
    )
    progress = fields.Float(
        string="Progress",
        compute='_compute_progress',
        store=True
    )

    @api.multi
    @api.depends(
        'task_ids.planned_hours')
    def _compute_planned_hours(self):
        for rec in self:
            hours = sum([task.planned_hours for task in rec.task_ids])
            rec.planned_hours = hours

    @api.multi
    @api.depends(
        'task_ids.total_hours_spent')
    def _compute_spent_hours(self):
        for rec in self:
            hours = sum([task.total_hours_spent for task in rec.task_ids])
            rec.total_hours_spent = hours

    @api.multi
    @api.depends(
        'total_hours_spent', 'planned_hours')
    def _compute_progress(self):
        for rec in self:
            progress = 0.0
            if rec.planned_hours:
                progress = rec.total_hours_spent / rec.planned_hours * 100.0
            rec.progress = progress
