# -*- coding: utf-8 -*-
# See README.rst file on addon root folder for license details

from openerp import models, api
from datetime import datetime, timedelta


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    @api.v7
    def get_working_days_of_date(self, cr, uid, id, start_dt=None, end_dt=None,
                                 leaves=None, compute_leaves=False,
                                 resource_id=None, default_interval=None,
                                 context=None):
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
                working_intervals = self.get_working_intervals_of_day(
                    cr, uid, id, start_dt=current, end_dt=end, leaves=leaves,
                    compute_leaves=compute_leaves, resource_id=resource_id,
                    default_interval=default_interval, context=context)
                if working_intervals:
                    days += 1
            next = current + timedelta(days=1)
            current = next
        return days
