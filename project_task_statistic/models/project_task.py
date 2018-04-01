# -*- coding: utf-8 -*-
# Copyright 2014 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from openerp import models, fields, api


class Task(models.Model):
    _inherit = 'project.task'

    @api.multi
    @api.depends(
        "stage_id", "create_date", "date_opened",
        "date_closed",
    )
    def _compute_statistic(self):
        for task in self:
            if task.create_date and task.date_opened:
                date_opened = datetime.strptime(
                    task.date_opened, "%Y-%m-%d %H:%M:%S")
                date_created = datetime.strptime(
                    task.create_date, "%Y-%m-%d %H:%M:%S")
                diff = date_opened - date_created
                task.day_open = diff.days
                task.hours_open = diff.total_seconds() / 3600.0
            if task.date_opened and task.date_closed:
                date_closed = datetime.strptime(
                    task.date_closed, "%Y-%m-%d %H:%M:%S")
                date_opened = datetime.strptime(
                    task.date_opened, "%Y-%m-%d %H:%M:%S")
                diff = date_closed - date_opened
                task.day_close = diff.days
                task.hours_close = diff.total_seconds() / 3600.0

    date_opened = fields.Datetime(
        string="Date Opened",
        )
    date_closed = fields.Datetime(
        string="Date Closed",
        )
    day_close = fields.Float(
        string="Days to Close",
        compute="_compute_statistic",
        store=True,
    )
    day_open = fields.Float(
        string="Days to Open",
        compute="_compute_statistic",
        store=True,
    )
    hours_close = fields.Float(
        string="Hours to Close",
        compute="_compute_statistic",
        store=True,
    )
    hours_open = fields.Float(
        string="Working Hours to Open",
        compute="_compute_statistic",
        store=True,
    )

    @api.multi
    def _calc_statistics(self):
        for task in self:
            is_open = task.stage_id.state == 'open'
            is_close = task.stage_id.state in ('cancelled', 'done')
            if is_open and not task.date_opened:
                # Task opened/started
                task.date_opened = fields.Datetime.now()
            if is_close and not task.date_closed:
                # Task closed (could move directly from draft to done!)
                task.date_closed = fields.Datetime.now()
                if not task.date_opened:
                    task.date_opened = task.date_closed
            if not is_close and task.date_closed:
                # Undoing task close
                task.date_closed = None

    @api.model
    def create(self, vals):
        task = super(Task, self).create(vals)
        task._calc_statistics()
        return task

    @api.multi
    def write(self, vals):
        _super = super(Task, self)
        _super.write(vals)
        if "stage_id" in vals:
            self._calc_statistics()
