# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime, time

import pytz
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import date_utils, mute_logger

_logger = logging.getLogger(__name__)


class ForecastLine(models.Model):
    """
    we generate 1 forecast line per period defined on the current company (day, week, month).
    """

    _name = "forecast.line"
    _order = "date_from, employee_id, project_id"
    _description = "Forecast"

    name = fields.Char(required=True)
    date_from = fields.Date(
        required=True, help="Date of the period start for this line"
    )
    date_to = fields.Date(required=True)
    forecast_role_id = fields.Many2one(
        "forecast.role", string="Forecast role", required=True, index=True
    )
    employee_id = fields.Many2one("hr.employee", string="Employee")
    employee_forecast_role_id = fields.Many2one(
        "hr.employee.forecast.role", string="Employee Forecast Role"
    )
    project_id = fields.Many2one("project.project", index=True, string="Project")
    task_id = fields.Many2one("project.task", index=True, string="Task")
    sale_id = fields.Many2one(
        "sale.order",
        related="sale_line_id.order_id",
        store=True,
        index=True,
        string="Sale",
    )
    sale_line_id = fields.Many2one("sale.order.line", index=True, string="Sale line")
    hr_leave_id = fields.Many2one("hr.leave", index=True, string="Leave")
    forecast_hours = fields.Float(
        "Forecast",
        help="Forecast (in hours). Forecast is positive for resources which add forecast, "
        "such as employees, and negative for things which consume forecast, such as "
        "holidays, sales, or tasks.",
    )
    cost = fields.Monetary(
        help="Cost, in company currency. Cost is positive for things which add forecast, "
        "such as employees and negative for things which consume forecast such as "
        "holidays, sales, or tasks. ",
    )
    consolidated_forecast = fields.Float(
        digits=(12, 5),
        store=True,
        compute="_compute_consolidated_forecast",
    )

    currency_id = fields.Many2one(related="company_id.currency_id", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda s: s.env.company
    )
    type = fields.Selection(
        [("forecast", "Forecast"), ("confirmed", "Confirmed")],
        required=True,
        default="forecast",
    )
    res_model = fields.Char(string="Model", index=True)
    res_id = fields.Integer(string="Record ID", index=True)
    employee_resource_forecast_line_id = fields.Many2one(
        "forecast.line",
        store=True,
        index=True,
        compute="_compute_employee_forecast_line_id",
        ondelete="set null",
        help="technical field giving the name of the resource "
        "(model=hr.employee.forecast.role) line for that employee and that period",
    )
    employee_resource_consumption_ids = fields.One2many(
        "forecast.line", "employee_resource_forecast_line_id"
    )

    @api.depends("employee_id", "date_from", "type", "res_model")
    def _compute_employee_forecast_line_id(self):
        employees = self.mapped("employee_id")
        date_froms = self.mapped("date_from")
        date_tos = self.mapped("date_to")
        if employees:
            lines = self.search(
                [
                    ("employee_id", "in", employees.ids),
                    ("res_model", "=", "hr.employee.forecast.role"),
                    ("date_from", ">=", min(date_froms)),
                    ("date_to", "<=", max(date_tos)),
                    ("type", "=", "confirmed"),
                ]
            )
        else:
            lines = self.env["forecast.line"]
        capacities = {}
        for line in lines:
            capacities[(line.employee_id.id, line.date_from)] = line.id
        for rec in self:
            if rec.type == "confirmed" and rec.res_model != "hr.employee.forecast.role":
                rec.employee_resource_forecast_line_id = capacities.get(
                    (rec.employee_id.id, rec.date_from), False
                )
            else:
                rec.employee_resource_forecast_line_id = False

    def _convert_forecast(self, data):
        """
        Converts consolidated forecast from hours to days
        """
        self.ensure_one()
        to_convert_uom = self.env.ref("uom.product_uom_day")
        project_time_mode_id = self.company_id.project_time_mode_id
        if self.res_model != "hr.employee.forecast.role":
            return -project_time_mode_id._compute_quantity(
                self.forecast_hours, to_convert_uom, round=False
            )
        else:
            forecast_hours = self.forecast_hours + data.get(self.id, 0)
            return project_time_mode_id._compute_quantity(
                forecast_hours, to_convert_uom, round=False
            )

    @api.depends("employee_resource_consumption_ids.forecast_hours", "forecast_hours")
    def _compute_consolidated_forecast(self):
        data = {}
        for d in self.env["forecast.line"].read_group(
            [("employee_resource_forecast_line_id", "in", self.ids)],
            fields=["forecast_hours"],
            groupby=["employee_resource_forecast_line_id"],
        ):
            data[d["employee_resource_forecast_line_id"][0]] = d["forecast_hours"]
        for rec in self:
            rec.consolidated_forecast = rec._convert_forecast(data)

    def prepare_forecast_lines(
        self,
        name,
        date_from,
        date_to,
        ttype,
        forecast_hours,
        unit_cost,
        res_model="",
        res_id=0,
        **kwargs
    ):
        common_value_dict = {
            "company_id": self.env.company.id,
            "name": name,
            "type": ttype,
            "forecast_role_id": kwargs.get("forecast_role_id", False),
            "employee_id": kwargs.get("employee_id", False),
            "project_id": kwargs.get("project_id", False),
            "task_id": kwargs.get("task_id", False),
            "sale_line_id": kwargs.get("sale_line_id", False),
            "hr_leave_id": kwargs.get("hr_leave_id", False),
            "employee_forecast_role_id": kwargs.get("employee_forecast_role_id", False),
            "res_model": res_model,
            "res_id": res_id,
        }
        forecast_line_vals = []
        if common_value_dict["employee_id"]:
            resource = (
                self.env["hr.employee"]
                .browse(common_value_dict["employee_id"])
                .resource_id
            )
            calendar = resource.calendar_id
        else:
            resource = self.env["resource.resource"]
            calendar = self.env.company.resource_calendar_id
        for updates in self._split_per_period(
            date_from, date_to, forecast_hours, unit_cost, resource, calendar
        ):
            values = common_value_dict.copy()
            values.update(updates)
            forecast_line_vals.append(values)
        return forecast_line_vals

    def _company_horizon_end(self):
        company = self.env.company
        today = fields.Date.context_today(self)
        horizon_end = today + relativedelta(months=company.forecast_line_horizon)
        return horizon_end

    def _split_per_period(
        self, date_from, date_to, forecast_hours, unit_cost, resource, calendar
    ):
        company = self.env.company
        today = fields.Date.context_today(self)
        granularity = company.forecast_line_granularity
        delta = date_utils.get_timedelta(1, granularity)
        horizon_end = self._company_horizon_end()
        # the date_to passed as argument is "included". We want to be able to
        # reason with this date "excluded" when doing substractions to compute
        # a number of days -> add 1d
        date_to += relativedelta(days=1)
        horiz_date_from = max(date_from, today)
        horiz_date_to = min(date_to, horizon_end)
        curr_date = date_utils.start_of(horiz_date_from, granularity)
        if horiz_date_to <= horiz_date_from:
            return
        whole_period_forecast = self._number_of_hours(
            horiz_date_from, horiz_date_to, resource, calendar
        )
        if whole_period_forecast == 0:
            # the resource if completely off during the period -> we cannot
            # plan the forecast in the period. We put the whole forecast on the
            # day after the period.
            # TODO future improvement: dump this on the
            # first day when the employee is not on holiday
            _logger.warning(
                "resource %s has 0 forecast on period %s -> %s",
                resource,
                horiz_date_from,
                horiz_date_to,
            )
            yield {
                "date_from": horiz_date_to,
                "date_to": horiz_date_to + delta - relativedelta(days=1),
                "forecast_hours": forecast_hours,
                "cost": forecast_hours * unit_cost,
            }
            return
        daily_forecast = forecast_hours / whole_period_forecast
        if daily_forecast == 0:
            return
        while curr_date < horiz_date_to:
            next_date = curr_date + delta
            # XXX fix periods which are not entirely in the horizon
            # (min max trick on the numerator of the division)
            period_forecast = self._number_of_hours(
                max(curr_date, date_from),
                min(next_date, date_to),
                resource,
                calendar,
            )
            # note we do create lines even if the period_forecast is 0, as this
            # ensures that consolidated capacity can be computed: if there is
            # no line for a day when the employee does not work, but for some
            # reason there is a need on that day, we need the 0 capacity line
            # to compute the negative consolidated capacity.
            period_forecast *= daily_forecast
            period_cost = period_forecast * unit_cost
            updates = {
                "date_from": curr_date,
                "date_to": next_date - relativedelta(days=1),
                "forecast_hours": period_forecast,
                "cost": period_cost,
            }
            yield updates
            curr_date = next_date

    @api.model
    def _cron_recompute_all(self, force_company_id=None):
        today = fields.Date.context_today(self)
        ForecastLine = self.env["forecast.line"].sudo()
        if force_company_id:
            companies = self.env["res.company"].browse(force_company_id)
        else:
            companies = self.env["res.company"].search([])
        for company in companies:
            ForecastLine = ForecastLine.with_company(company)
            limit_date = date_utils.start_of(today, company.forecast_line_granularity)
            stale_forecast_lines = ForecastLine.search(
                [
                    ("date_from", "<", limit_date),
                    ("company_id", "=", company.id),
                ]
            )
            stale_forecast_lines.unlink()

        # always start with forecast role to ensure we can compute the
        # employee_resource_forecast_line_id field
        self.env["hr.employee.forecast.role"]._recompute_forecast_lines(
            force_company_id=force_company_id
        )
        self.env["sale.order.line"]._recompute_forecast_lines(
            force_company_id=force_company_id
        )
        self.env["hr.leave"]._recompute_forecast_lines(
            force_company_id=force_company_id
        )
        self.env["project.task"]._recompute_forecast_lines(
            force_company_id=force_company_id
        )
        # fix weird issue where the employee_resource_forecast_line_id seems to
        # not be always computed
        ForecastLine.search([])._compute_employee_forecast_line_id()

    @api.model
    def convert_days_to_hours(self, days):
        uom_day = self.env.ref("uom.product_uom_day")
        uom_hour = self.env.ref("uom.product_uom_hour")
        return uom_day._compute_quantity(days, uom_hour)

    @api.model
    def _number_of_hours(self, date_from, date_to, resource, calendar):
        tzinfo = pytz.timezone(calendar.tz)
        start_dt = tzinfo.localize(datetime.combine(date_from, time(0)))
        end_dt = tzinfo.localize(datetime.combine(date_to, time(0)))
        intervals = calendar._work_intervals_batch(
            start_dt, end_dt, resources=resource
        )[resource.id]
        nb_hours = sum(
            (stop - start).total_seconds() / 3600 for start, stop, meta in intervals
        )
        return nb_hours

    def unlink(self):
        # we routinely unlink forecast lines, let"s not fill the logs with this
        with mute_logger("odoo.models.unlink"):
            return super().unlink()
