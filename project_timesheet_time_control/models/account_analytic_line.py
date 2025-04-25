# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2025 glueckkanja AG - Christopher Rogos

# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime, time, timedelta

import pytz
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    _order = "date_time desc"

    @api.model
    def _get_default_start_time(self):
        # Set the default start time according to setting to now
        # or after the previous entry.
        params = self.env["ir.config_parameter"].sudo()
        timesheet_alignment = params.get_param(
            "project_timesheet_time_control.timesheet_alignment"
        )
        # default to now
        now = fields.Datetime.now()
        start_time = datetime.combine(
            now.date(), time(hour=now.hour, minute=now.minute, second=0)
        )
        if timesheet_alignment == "now":
            return start_time
        defaults = self.default_get(["employee_id", "company_id", "date"])
        date_day = defaults.get("date", now.date())
        employee_id = defaults.get(
            "employee_id",
            self._context.get("default_employee_id", self.env.user.employee_id.id),
        )
        if not employee_id:
            return start_time
        # get the last entry of the employee on the same day
        # (searching for date_time_end would be better, but is not working)
        analytic_lines = self.env[self._name].search(
            [
                ["employee_id", "=", employee_id],
                ["date", "=", date_day],
                ["date_time", "!=", False],
            ],
            order="date_time desc",
            limit=1,
        )
        if analytic_lines.date_time_end:
            start_time = analytic_lines.date_time_end
        if not analytic_lines:
            # if employee has no analytic_lines at this day,
            # get the employee calendar and set the start time
            # to the first interval of the day
            employee = self.env["hr.employee"].browse(employee_id)
            if employee.resource_calendar_id:
                start_date = datetime.combine(
                    date_day, time(0, tzinfo=pytz.timezone(employee.tz))
                )
                end_date = start_date + timedelta(days=1)
                intervals = employee.resource_calendar_id._work_intervals_batch(
                    start_date, end_date
                ).get(False, False)
                if intervals and intervals._items:
                    start_time = (
                        intervals._items[0][0].astimezone(pytz.UTC).replace(tzinfo=None)
                    )
        return start_time

    date_time = fields.Datetime(
        string="Start Time", default=_get_default_start_time, copy=False
    )
    date_time_end = fields.Datetime(
        string="End Time",
        compute="_compute_date_time_end",
        inverse="_inverse_date_time_end",
    )
    show_time_control = fields.Selection(
        selection=[("resume", "Resume"), ("stop", "Stop")],
        compute="_compute_show_time_control",
        help="Indicate which time control button to show, if any.",
    )

    unit_amount_hours = fields.Float(
        compute="_compute_unit_amount",
    )

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        if (
            self._context.get("is_timesheet", False)
            and "product_uom_id" in fields_list
            and "product_uom_id" not in vals
        ):
            company_id = vals.get("company_id")
            company = False
            if company_id:
                company = self.env["res.company"].browse(company_id)
            if not company:
                employee_in_id = vals.get(
                    "employee_id", self._context.get("default_employee_id", False)
                )
                if employee_in_id:
                    company = self.env["hr.employee"].browse(employee_in_id).company_id
                else:
                    company = self.env["res.company"].browse(self.env.company.id)

            if "company_id" in fields_list:
                vals["company_id"] = company.id

            if company and not vals.get("product_uom_id"):
                vals["product_uom_id"] = company.project_time_mode_id.id

        return vals

    @api.depends("unit_amount", "product_uom_id", "date_time")
    def _compute_date_time_end(self):
        hour_uom = self.env.ref("uom.product_uom_hour")
        for record in self:
            if record.product_uom_id == hour_uom and record.date_time:
                # When unit_amount is not set, the date_time_end is updated
                record.date_time_end = record.date_time + relativedelta(
                    hours=record.unit_amount
                )
            else:
                record.date_time_end = record.date_time_end

    @api.depends("product_uom_id", "date_time", "date_time_end")
    def _compute_unit_amount(self):
        hour_uom = self.env.ref("uom.product_uom_hour")
        for record in self:
            if (
                record.product_uom_id == hour_uom
                and record.date_time_end
                and record.date_time
            ):
                # When date_time_end or date_time is not set, the unit_amount is updated
                record.unit_amount = (
                    record.date_time_end - record.date_time
                ).total_seconds() / 3600
                record.unit_amount_hours = record.unit_amount
            else:
                record.unit_amount_hours = 0.0

    def _inverse_date_time_end(self):
        hour_uom = self.env.ref("uom.product_uom_hour")
        for record in self.filtered(lambda x: x.date_time and x.date_time_end):
            if record.product_uom_id == hour_uom:
                record.unit_amount = (
                    record.date_time_end - record.date_time
                ).total_seconds() / 3600

    @api.model
    def _eval_date(self, vals):
        if vals.get("date_time"):
            return dict(vals, date=self._convert_datetime_to_date(vals["date_time"]))
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

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(list(map(self._eval_date, vals_list)))

    def write(self, vals):
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

    def button_end_work(self):
        end = fields.Datetime.to_datetime(
            self.env.context.get("stop_dt", datetime.now())
        )
        for line in self:
            if line.unit_amount:
                raise UserError(
                    _(
                        "Cannot stop timer %d because it is not running. "
                        "Refresh the page and check again."
                    )
                    % line.id
                )
            line.unit_amount = line._duration(line.date_time, end)
        return True
