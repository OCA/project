# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectProject(models.Model):

    _inherit = 'project.project'

    planned_hours = fields.Float(
        string="Planned hours", compute='_compute_hours', store=True)
    total_hours_spent = fields.Float(
        string="Total hours spent", compute='_compute_hours', store=True)
    progress = fields.Float(
        string="Progress", compute='_compute_hours', store=True)

    @api.multi
    @api.depends(
        'task_ids.planned_hours', 'task_ids.total_hours_spent')
    def _compute_hours(self):
        for rec in self:
            rec.planned_hours = rec._get_planned_hours()
            rec.total_hours_spent = rec._get_total_hours_spent()
            rec.progress = rec._get_progress()

    @api.multi
    def _get_planned_hours(self):
        self.ensure_one()
        return sum([task.planned_hours for task in self.task_ids])

    @api.multi
    def _get_total_hours_spent(self):
        self.ensure_one()
        return sum([task.total_hours_spent for task in self.task_ids])

    @api.multi
    def _get_progress(self):
        self.ensure_one()
        progress = 0.0
        if self.planned_hours > 0.0:
            progress = round(
                100.0 * (self.total_hours_spent) / self.planned_hours, 2)
        return progress
