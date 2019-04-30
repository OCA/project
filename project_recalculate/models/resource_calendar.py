# -*- coding: utf-8 -*-
# See README.rst file on addon root folder for license details

from odoo import models
from datetime import datetime, timedelta


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def get_working_days_of_date(self, start_dt=None, end_dt=None,
                                 leaves=None, compute_leaves=False,
                                 resource_id=None, default_interval=None):
        self.ensure_one()
        if start_dt is None:
            start_dt = datetime.now().replace(hour=0, minute=0, second=0)
        if end_dt is None:
            end_dt = datetime.now().replace(hour=23, minute=59, second=59)
        days = 0
        current = start_dt
        while current <= end_dt:
            if id is None:
                days += 1
            else:
                end_day = current.replace(hour=23, minute=59, second=59)
                end = end_dt if end_day > end_dt else end_day
                obj = self.with_context(tz='UTC')
                working_intervals = obj.get_working_intervals_of_day(
                    start_dt=current, end_dt=end, leaves=leaves,
                    compute_leaves=compute_leaves, resource_id=resource_id,
                    default_interval=default_interval,
                )
                if working_intervals:
                    days += 1
            next_dt = current + timedelta(days=1)
            current = next_dt
        return days
