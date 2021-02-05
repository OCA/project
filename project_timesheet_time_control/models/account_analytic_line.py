# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime
from pytz import timezone, UTC

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons.resource.models.resource import float_to_time


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _order = 'date_time desc'

    date_time = fields.Datetime(
        default=fields.Datetime.now,
        copy=False,
    )
    show_time_control = fields.Selection(
        selection=[("resume", "Resume"), ("stop", "Stop")],
        compute="_compute_show_time_control",
        help="Indicate which time control button to show, if any.",
    )

    @api.model
    def _eval_date(self, vals):
        if vals.get('date_time'):
            return dict(vals, date=self._convert_datetime_to_date(vals['date_time']))
        return vals

    def _convert_datetime_to_date(self, datetime_):
        if isinstance(datetime_, str):
            datetime_ = fields.Datetime.from_string(datetime_)
        return fields.Date.context_today(self, datetime_)

    @api.model
    def _running_domain(self):
        """Domain to find running timesheet lines."""
        return [
            ("date_time", "!=", False),
            ("user_id", "=", self.env.user.id),
            ("project_id.allow_timesheets", "=", True),
            ("unit_amount", "=", 0),
        ]

    @api.model
    def _duration(self, start, end):
        """Compute float duration between start and end."""
        try:
            return (end - start).total_seconds() / 3600
        except TypeError:
            return 0

    @api.depends("employee_id", "unit_amount")
    def _compute_show_time_control(self):
        """Decide when to show time controls."""
        for one in self:
            if one.employee_id not in self.env.user.employee_ids:
                one.show_time_control = False
            elif one.unit_amount or not one.date_time:
                one.show_time_control = "resume"
            else:
                one.show_time_control = "stop"

    @api.model
    def _get_employee_start_time(self, employee_id, date):
        """Get datetime from date using employee calendars attendance"""
        employee_timezone = timezone(employee_id.tz or 'UTC')
        calendar = employee_id.resource_calendar_id
        for attendance in calendar.attendance_ids:
            weekday = int(attendance.dayofweek)
            if weekday == date.weekday():
                time = float_to_time(attendance.hour_from)
                dt_user = datetime.combine(date, time)
                dt_server = employee_timezone.localize(dt_user).astimezone(UTC)
                return fields.Datetime.to_string(dt_server)
        return False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Set or override date from date_time to avoid inconsistent state
            if vals.get('date_time'):
                vals.update(self._eval_date(vals))
            # If no date_time is provided, made an attempt to guess the
            # start time from employee calendar if set at the same time
            if vals.get('date') and not vals.get('date_time'):
                date = fields.Date.from_string(vals.get('date'))
                if vals.get('employee_id'):
                    employee_id = self.env['hr.employee'].browse(
                        vals.get('employee_id')
                    )
                elif self.env.user.employee_ids:
                    employee_id = self.env.user.employee_ids[0]
                else:
                    employee_id = False
                if employee_id:
                    date_time = self._get_employee_start_time(employee_id, date)
                    if date_time:
                        vals['date_time'] = date_time
        return super().create(vals_list)

    @api.multi
    def write(self, vals):
        if 'date' in vals and 'date_to_date_time' not in self.env.context:
            date = fields.Date.from_string(vals.get('date'))
            for rec in self.with_context(date_to_date_time=True):
                time = self.date_time.time()
                rec.write({'date_time': datetime.combine(date, time)})
        return super().write(self._eval_date(vals))

    def button_resume_work(self):
        """Create a new record starting now, with a running timer."""
        return {
            "name": _("Resume work"),
            "res_model": "hr.timesheet.switch",
            "target": "new",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
        }

    @api.multi
    def button_end_work(self):
        end = fields.Datetime.to_datetime(
            self.env.context.get("stop_dt", datetime.now()))
        for line in self:
            if line.unit_amount:
                raise UserError(
                    _("Cannot stop timer %d because it is not running. "
                      "Refresh the page and check again.") %
                    line.id
                )
            line.unit_amount = line._duration(line.date_time, end)
        return True
