# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _calendar_schedule_hours(self, hours, day_date,
                                 resource=None, calendar=None):
        if not day_date:
            return False, False
        default_interval = self._interval_default_get()
        intervals = calendar.schedule_hours(
            hours, day_dt=day_date, compute_leaves=True,
            resource_id=resource.id, default_interval=default_interval,
        )
        return (intervals and intervals[0] or False,
                intervals and intervals[-1] or False)

    @api.multi
    def task_recalculate(self, calculation_type, start_task=False,
                         end_date=False, start_date=False, planned_hours=False,
                         user=False):
        """Recalculate task start date and end date depending on
        project calculation_type, planned_hours, user_id and sequence.
        """
        to_string = fields.Datetime.to_string
        from_string = fields.Datetime.from_string
        reverse = False
        if calculation_type == 'date_end':
            reverse = True
        if not user:
            user = self.mapped('user_id')
        for user_id in user:
            date_start = False
            date_end = False
            project_date = False
            tasks_todo = self.filtered(
                lambda x: x.stage_id and x.include_in_recalculate and
                x.user_id == user_id and x.planned_hours).sorted(
                    key='sequence', reverse=reverse)
            if start_task:
                tasks_todo = start_task + tasks_todo
                date_start = from_string(
                    start_date and start_date or start_task.date_start)
                date_end = from_string(
                    end_date and end_date or start_task.date_end)
                project_date = date_start
            for task in tasks_todo:
                resource, calendar = task._resource_calendar_select()
                if not resource or not calendar:
                    continue
                if not planned_hours:
                    planned_hours = task.planned_hours
                if not project_date:
                    not_used, project_date, not_used = task.\
                        _calculation_prepare()
                    interval = task._first_interval_of_day_get(
                        project_date, resource=resource, calendar=calendar)
                    if interval:
                        project_date = interval[0]
                start = task._calendar_schedule_hours(
                    planned_hours * -1,
                    date_start if reverse and date_start
                    else project_date,
                    resource, calendar)[0] if reverse \
                    else date_end if date_end and not start_task == task \
                    else project_date
                end = task._calendar_schedule_hours(
                    planned_hours,
                    date_end if not reverse and date_end
                    else project_date,
                    resource, calendar)[-1] if not (
                        reverse or start_task == task) \
                    else date_end if start_task == task else date_start if\
                    date_start else project_date
                if start:
                    date_start = start if isinstance(start, datetime) \
                        else start[0]
                if end:
                    date_end = end if isinstance(end, datetime) else end[-1]
                task.with_context(
                    task.env.context, task_recalculate=True).write({
                        'date_start': date_start and to_string(date_start)
                        or False,
                        'date_end': date_end and to_string(date_end) or False,
                        'date_deadline': date_end and to_string(date_end)
                        or False,
                    })
                planned_hours = False
        return True

    @api.multi
    def write(self, vals):
        if 'task_recalculate' not in self.env.context:
            # NOT IMPLEMENTED or 'sequence' in vals:
            if vals.get('date_end') or vals.get('date_start') \
                    or vals.get('planned_hours') or vals.get('user_id'):
                for task in self:
                    # pass only task after this one for this user (and
                    # dependencies tasks when implemented) and calculate always
                    # as date_begin - the user has modified a single task
                    task.project_id.tasks.filtered(
                        lambda x: x.sequence > task.sequence and
                        x.user_id == task.user_id  # and x.task dependencies ..
                    ).task_recalculate(
                        calculation_type='date_begin',
                        start_task=task,
                        end_date=vals.get('date_end'),
                        start_date=vals.get('date_start'),
                        planned_hours=vals.get('planned_hours'),
                        user=vals.get('user_id'))
        return super(ProjectTask, self).write(vals)

    def _dates_onchange(self, vals):
        return vals

    def _estimated_days_prepare(self, vals):
        return vals
