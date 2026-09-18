# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from datetime import timedelta

from bokeh import palettes
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import date_utils
from odoo.tools.misc import get_lang


class ForecastLineReporting(models.TransientModel):
    _name = "forecast.line.reporting"
    _description = "Forecast reporting wizard"

    bokeh_chart = fields.Text(compute="_compute_bokeh_chart")
    date_from = fields.Date(default=fields.Date.today)
    nb_months = fields.Integer(default=2)
    granularity = fields.Selection(
        [("day", "Day"), ("week", "Week"), ("month", "Month")],
        default=lambda r: r.env.company.forecast_line_granularity,
        required=True,
    )

    employee_ids = fields.Many2many("hr.employee")

    project_ids = fields.Many2many(
        "project.project",
        help="Setting this will automatically add "
        "all employees assigned to tasks on the project",
    )

    @api.onchange("project_ids")
    def onchange_project_ids(self):
        if self.project_ids:
            self.employee_ids |= self.project_ids.mapped(
                "task_ids.user_ids.employee_ids"
            )

    @api.depends("date_from", "nb_months", "employee_ids", "granularity", "project_ids")
    def _compute_bokeh_chart(self):
        """compute the chart to be displayed"""
        # the current implementation shows 1 chart per selected employee over
        # the next nb_month months with the selected granularity. For each
        # employee, the chart displays the consolidated_forecast field
        # grouped by project on which the employee is planned for a given
        # period.
        for rec in self:
            plots = rec._build_plots()
            grid = column(*plots)
            script, div = components(grid, wrap_script=False)
            rec.bokeh_chart = json.dumps({"div": div, "script": script})

    def _prepare_bokeh_chart_data(self):
        """compute the data that will be plotted.

        :return: a tuple with 2 elements: (projects list, plot_data
        dictionary).

        The plot data dictionary is nested dictionary defined as follows:

        {
            employee: {
                project: {
                    date: forecast
                    for dates with a forecast on that project
                }
                for all projects scheduled on employee
            }
            for all selected employees
        }

        """
        end_date = self.date_from + relativedelta(months=self.nb_months)
        domain = [
            ("date_from", ">=", self.date_from),
            ("date_to", "<=", end_date),
        ]
        if self.employee_ids:
            if self.project_ids:
                domain += [
                    "|",
                    "&",
                    ("employee_id", "=", False),
                    ("project_id", "in", self.project_ids.ids),
                    ("employee_id", "in", self.employee_ids.ids),
                ]
            else:
                domain += [("employee_id", "in", self.employee_ids.ids)]
        else:
            domain.append(("employee_id", "=", False))
        date_spec = f"date_from:{self.granularity}"
        groupdata = self.env["forecast.line"]._read_group(
            domain,
            groupby=[date_spec, "employee_id", "project_id"],
            aggregates=["consolidated_forecast:sum"],
        )
        employees = set()
        projects = set()
        data_project = {}
        data_overload = {}
        not_assigned = self.env._("Not assigned to an employee")
        available = self.env._("Available")
        overload = self.env._("Overload")
        for date, employee_rec, project_rec, forecast in groupdata:
            employee = employee_rec.name if employee_rec else not_assigned
            employees.add(employee)
            if employee not in data_project:
                data_project[employee] = {}
                data_overload[employee] = {}
            if project_rec:
                project = project_rec.name
                data = data_project
            elif forecast >= 0:
                project = available
                data = data_project
            else:
                project = overload
                data = data_overload
            projects.add(project)
            if project not in data[employee]:
                data[employee][project] = {}
            x_key = date.strftime("%Y-%m-%d")
            data[employee][project][x_key] = forecast
        employees = list(employees)
        employees.sort()
        if not_assigned in employees:
            # make sure it is the last one
            employees.remove(not_assigned)
            employees.append(not_assigned)
        projects = list(projects)
        projects.sort()
        for name in [available, overload]:
            if name in projects:
                # make sure these two get in the first tow positions
                projects.remove(name)
                projects.insert(0, name)
        return employees, projects, data_project, data_overload

    def _get_time_range(self):
        end_date = self.date_from + relativedelta(months=self.nb_months)
        dates = []
        granularity = self.granularity
        # start from the truncated period start, matching the DB-side
        # date_trunc() done by the date_from:<granularity> groupby, so the
        # x-axis keys line up with the group keys for week/month too.
        # _read_group's week grouping is anchored on the language's first
        # day of the week (res.lang.week_start, Sunday for en_US), not on
        # the ISO/Monday convention date_utils.start_of() always uses.
        if granularity == "week":
            first_week_day = int(get_lang(self.env).week_start) - 1
            date = self.date_from - timedelta(
                days=(self.date_from.weekday() - first_week_day) % 7
            )
        else:
            date = date_utils.start_of(self.date_from, granularity)
        delta = date_utils.get_timedelta(1, granularity)
        while date < end_date:
            dates.append(date.strftime("%Y-%m-%d"))
            date += delta
        return dates

    def _build_empty_plot(self, height=300, width=1024):
        dates = self._get_time_range()
        p = figure(height=height, width=width, x_range=FactorRange(*dates))
        p.title.text = self.env._("Nothing to plot. Select some employees")
        return [p]

    def _get_palette(self, projects):
        """return a dictionary mapping project names to colors"""
        if len(projects) <= 20:
            project_colors = palettes.Category20[max(len(projects), 3)][: len(projects)]
        else:
            step = len(palettes.Turbo256) // len(projects)
            project_colors = palettes.Turbo256[::step][: len(projects)]
        return dict(zip(projects, project_colors, strict=False))

    def _build_plots(self, height=300, width=1024):
        employees, projects, data, data_overload = self._prepare_bokeh_chart_data()
        if not data:
            return self._build_empty_plot(height, width)
        project_color_map = self._get_palette(projects)
        dates = self._get_time_range()
        plots = []
        for employee in employees:
            plot_data = {"dates": dates}
            plot_data_overload = {"dates": dates}
            for project in data[employee]:
                forecast = data[employee][project]
                plot_data[project] = [forecast.get(date, 0) for date in dates]
            for project in data_overload[employee]:
                forecast = data_overload[employee][project]
                plot_data_overload[project] = [forecast.get(date, 0) for date in dates]
            plot_projects = [
                p
                for p in projects
                if p in data[employee] or p in data_overload[employee]
            ]
            source = ColumnDataSource(data=plot_data)
            source_overload = ColumnDataSource(data=plot_data_overload)
            p = figure(
                x_range=FactorRange(*dates),
                height=max(height, len(plot_projects) * 30),
                width=width,
            )
            for src in (source, source_overload):
                p.vbar_stack(
                    plot_projects,
                    x="dates",
                    source=src,
                    width=0.4,
                    alpha=0.5,
                    color=[project_color_map[p] for p in plot_projects],
                    legend_label=[
                        (proj_name if len(proj_name) < 20 else proj_name[:19] + "…")
                        for proj_name in plot_projects
                    ],
                )
            p.xaxis.major_label_orientation = "vertical"
            p.title.text = employee
            p.legend.click_policy = "mute"
            p.add_layout(p.legend[0], "right")
            plots.append(p)
        return plots
