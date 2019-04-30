# -*- coding: utf-8 -*-
# Copyright 2015 Antonio Espinosa
# Copyright 2015 Endika Iglesias
# Copyright 2015 Javier Espìnosa
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo import models, fields, api, _
from datetime import datetime


class ProjectTask(models.Model):
    _inherit = 'project.task'

    from_days = fields.Integer(
        string='From days',
        help='Anticipation days from date begin or date end', default=0)
    estimated_days = fields.Integer(
        string='Estimated days', help='Estimated days to end', default=1,
        oldname='anticipation_days')
    include_in_recalculate = fields.Boolean(
        related="stage_id.include_in_recalculate", readonly=True,
    )

    @api.constrains('estimated_days')
    def _estimated_days_check(self):
        for task in self:
            if task.estimated_days <= 0:
                raise exceptions.ValidationError(
                    _('Estimated days must be greater than 0.')
                )

    def _dates_onchange(self, vals):
        """
            Try to calculate estimated_days and from_days fields
            when date_start or date_end change.

            Dates fields (date_start, date_end) have preference to
            estimated_days and from_days
            except if context['task_recalculate'] == True, in other words,
            except if this change is done because task recalculating.
        """
        self.ensure_one()
        # If no date changes, do nothing
        if 'date_start' not in vals and 'date_end' not in vals:
            return vals
        # If we are changing dates because of task recalculating, do nothing
        if self.env.context.get('task_recalculate'):
            return vals
        date_start = vals.get('date_start', self.date_start)
        date_end = vals.get('date_end', self.date_end)
        # If any date is False, can't calculate estimated_days nor from_days
        if not date_start or not date_end:
            return vals
        from_string = fields.Datetime.from_string
        start = from_string(date_start)
        end = from_string(date_end)
        resource, calendar = self._resource_calendar_select()
        if end < start or not resource or not calendar:
            return vals
        default_interval = self._interval_default_get()
        # Calculate estimated_day
        vals['estimated_days'] = calendar.get_working_days_of_date(
            start_dt=start, end_dt=end, compute_leaves=True,
            default_interval=default_interval, resource_id=resource.id,
        )
        # Calculate from_days depending on project calculation type
        calculation_type = self.project_id.calculation_type
        if calculation_type:
            invert = False
            increment = calculation_type == 'date_begin'
            if increment:
                if not self.project_id.date_start:
                    # Can't calculate from_days without project date_start
                    return vals
                project_date = from_string(self.project_id.date_start)
                start, end = project_date, start
            else:
                if not self.project_id.date:
                    # Can't calculate from_days without project date
                    return vals
                project_date = from_string(self.project_id.date)
                start, end = start, project_date
            if end < start:
                invert = True
                start, end = end, start
            from_days = calendar.get_working_days_of_date(
                start_dt=start, end_dt=end, compute_leaves=True,
                default_interval=default_interval, resource_id=resource.id,
            )
            if invert and from_days:
                from_days = from_days * (-1)
            from_days = self._from_days_enc(
                from_days, project_date, resource, calendar, increment)
            vals['from_days'] = from_days
        return vals

    def _estimated_days_prepare(self, vals):
        # estimated_days must be greater than zero, if not defaults to 1
        if 'estimated_days' in vals and vals['estimated_days'] < 1:
            vals['estimated_days'] = 1
        return vals

    def _resource_calendar_select(self):
        """
            Select working calendar and resource related this task:
            Working calendar priority:
                - project
                - user
                - company
        """
        self.ensure_one()
        resource = False
        if self.user_id:
            # Get first resource of assigned user
            resource = self.env['resource.resource'].search(
                [('user_id', '=', self.user_id.id)], limit=1)
        if self.project_id.resource_calendar_id:
            # Get calendar from project
            calendar = self.project_id.resource_calendar_id
        elif resource and resource.calendar_id:
            # Get calendar from assigned user
            calendar = resource.calendar_id
        else:
            # Get calendar from company
            if self.user_id.company_id:
                # Get company from assigned user
                company = self.user_id.company_id
            else:
                # If not assigned user, get company from current user
                company = self.env.user.company_id
            calendar = self.env['resource.calendar'].search(
                [('company_id', '=', company.id)], limit=1)
        return resource, calendar

    def _from_days_enc(self, from_days, project_date,
                       resource=None, calendar=None, increment=True):
        interval = self._first_interval_of_day_get(
            project_date, resource=resource, calendar=calendar)
        # If project_date is holidays
        if not interval:
            if from_days > 0 and increment:
                from_days += 1
            elif from_days < 0 and not increment:
                from_days -= 1
            elif from_days == 0:
                from_days = 1 if increment else -1
        return from_days

    def _from_days_dec(self, from_days, project_date,
                       resource=None, calendar=None, increment=True):
        if from_days == 0:
            return 1 if increment else -1
        interval = self._first_interval_of_day_get(
            project_date, resource=resource, calendar=calendar)
        # If project_date is not holidays
        if interval:
            if from_days > 0:
                from_days += 1
            elif from_days < 0:
                from_days -= 1
        return from_days

    def _calculation_prepare(self):
        """
            Prepare calculation parameters:
                - Increment=True, when task date_start is after project date
                - Increment=False, when task date_start if before project date
                - project_date, reference project date
        """
        self.ensure_one()
        from_string = fields.Datetime.from_string
        increment = self.project_id.calculation_type == 'date_begin'
        if increment:
            if not self.project_id.date_start:
                raise exceptions.UserError(
                    _('Start Date field must be defined.')
                )
            project_date = from_string(self.project_id.date_start)
            days = self.from_days
        else:
            if not self.project_id.date:
                raise exceptions.UserError(
                    _('End Date field must be defined.')
                )
            project_date = from_string(self.project_id.date)
            days = self.from_days * (-1)
        return increment, project_date, days

    def _interval_context_tz(self, interval):
        start = datetime.now().replace(hour=interval[0])
        start = fields.Datetime.context_timestamp(self, start)
        end = datetime.now().replace(hour=interval[1])
        end = fields.Datetime.context_timestamp(self, end)
        return (start.hour, end.hour)

    def _interval_default_get(self):
        default = (8, 18)
        return self._interval_context_tz(default)

    def _first_interval_of_day_get(self, day_date, resource=None,
                                   calendar=None):
        default_interval = self._interval_default_get()
        intervals = calendar.get_working_intervals_of_day(
            start_dt=day_date, compute_leaves=True, resource_id=resource.id,
            default_interval=default_interval,
        )
        return intervals and intervals[0] or False

    def _calendar_schedule_days(self, days, day_date,
                                resource=None, calendar=None):
        if not day_date:
            return (False, False)
        default_interval = self._interval_default_get()
        intervals = calendar.schedule_days(
            days, day_date=day_date, compute_leaves=True,
            resource_id=resource.id, default_interval=default_interval,
        )
        return (intervals and intervals[0] or False,
                intervals and intervals[-1] or False)

    @api.multi
    def task_recalculate(self):
        """Recalculate task start date and end date depending on
        project calculation_type, estimated_days and from_days.
        """
        to_string = fields.Datetime.to_string
        for task in self.filtered('include_in_recalculate'):
            resource, calendar = task._resource_calendar_select()
            if not resource or not calendar:
                continue
            increment, project_date, from_days = task._calculation_prepare()
            date_start = False
            date_end = False
            from_days = self._from_days_dec(
                from_days, project_date, resource, calendar, increment)
            start = self._calendar_schedule_days(
                from_days, project_date, resource, calendar)[1]
            if start:
                day = start[0].replace(hour=0, minute=0, second=0)
                first = self._first_interval_of_day_get(
                    day, resource, calendar)
                if first:
                    date_start = first[0]
            if date_start:
                end = self._calendar_schedule_days(
                    task.estimated_days, date_start, resource, calendar)[1]
                if end:
                    date_end = end[1]
            task.with_context(task.env.context, task_recalculate=True).write({
                'date_start': date_start and to_string(date_start) or False,
                'date_end': date_end and to_string(date_end) or False,
                'date_deadline': date_end and to_string(date_end) or False,
            })
        return True

    @api.multi
    def write(self, vals):
        for this in self:
            vals = this._dates_onchange(vals)
            vals = this._estimated_days_prepare(vals)
            super(ProjectTask, this).write(vals)
        return True
