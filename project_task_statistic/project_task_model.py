# -*- coding: utf-8 -*-
# Copyright 2014 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class Task(models.Model):
    _inherit = 'project.task'

    date_opened = fields.Datetime('Date Opened')
    date_closed = fields.Datetime('Date Closed')

    # TODO: enable same statistic fields available for Issues
    # day_close = fields.Float('Days to Close')
    # day_open = fields.Float('Days to Open')
    # working_hours_close = fields.Float('Working Hours to Close')
    # working_hours_open = fields.Float('Working Hours to Open')

    @api.multi
    def _calc_statistics(self):
        for task in self:
            is_open = self.stage_id.state == 'open'
            is_close = self.stage_id.state in ('cancelled', 'done')
            if is_open and not self.date_opened:
                # Task opened/started
                self.date_opened = fields.Datetime.now().to_string()
            if is_close and not self.date_closed:
                # Task closed (could move directly from draft to done!)
                self.date_closed = fields.Datetime.now().to_string()
                if not self.date_opened:
                    self.date_opened = self.date_closed
            if not is_close and self.date_closed:
                # Undoing task close
                self.date_closed = None

    @api.model
    def create(self, vals):
        task = super(Task, self).create(vals)
        task._calc_statistics()
        return task

    @api.multi
    def write(self, vals):
        tasks = super(Task, self).write(vals)
        tasks._calc_statistics()
        return tasks
