# See README.rst file on addon root folder for license details

from datetime import datetime, timedelta
from functools import partial

from odoo import models

from odoo.addons.resource.models.resource import make_aware


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def get_working_days_of_date(self, start_dt=None, end_dt=None, resource=None):
        self.ensure_one()
        if start_dt is None:
            start_dt = datetime.now().replace(hour=0, minute=0, second=0)
        if end_dt is None:
            end_dt = datetime.now().replace(hour=23, minute=59, second=59)
        days = 0
        current = start_dt
        while current <= end_dt:
            end_day = current.replace(hour=23, minute=59, second=59)
            end = end_dt if end_day > end_dt else end_day
            obj = self.with_context(tz="UTC")
            working_intervals = obj._work_intervals(current, end, resource)
            if len(working_intervals):
                days += 1
            current += timedelta(days=1)
        return days

    def plan_days_to_resource(
        self, days, day_dt, compute_leaves=False, resource=None, domain=None
    ):
        day_dt, revert = make_aware(day_dt)

        # which method to use for retrieving intervals
        if compute_leaves:
            get_intervals = partial(
                self._work_intervals, resource=resource, domain=domain
            )
        else:
            get_intervals = partial(self._attendance_intervals, resource=resource)

        if days > 0:
            found = set()
            delta = timedelta(days=14)
            for n in range(100):
                dt = day_dt + delta * n
                for start, stop, meta in get_intervals(dt, dt + delta):  # noqa: B007
                    found.add(start.date())
                    if len(found) == days:
                        return revert(stop)
            return False

        elif days < 0:
            days = abs(days)
            found = set()
            delta = timedelta(days=14)
            for n in range(100):
                dt = day_dt - delta * n
                for start, stop, meta in reversed(  # noqa: B007
                    get_intervals(dt - delta, dt)
                ):
                    found.add(stop.date())
                    if len(found) == days:
                        return revert(start)
            return False

        else:
            return revert(day_dt)
