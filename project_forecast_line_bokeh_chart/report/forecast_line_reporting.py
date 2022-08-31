# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

# pylint: disable=W7936
from bokeh import palettes
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.tools import date_utils


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
        plots = self._build_plots()
        grid = column(*plots)
        script, div = components(grid, wrap_script=False)
        self.bokeh_chart = json.dumps({"div": div, "script": script})

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
        groups = [
            "date_from:%s" % self.granularity,
            "employee_id",
            "project_id",
        ]
        groupdata = self.env["forecast.line"].read_group(
            domain, ["consolidated_forecast"], groups, lazy=False
        )
        employees = set()
        projects = set()
        data_project = {}
        data_overload = {}
        for d in groupdata:
            employee = d.get("employee_id")
            if employee:
                employee = employee[1]._value
            else:
                employee = _("Not assigned to an employee")
            employees.add(employee)
            if employee not in data_project:
                data_project[employee] = {}
                data_overload[employee] = {}
            forecast = d["consolidated_forecast"]
            date = d["__range"]["date_from"]["from"]
            project = d.get("project_id")
            if project:
                project = project[1]._value
                data = data_project
            elif forecast >= 0:
                project = _("Available")
                data = data_project
            else:
                project = _("Overload")
                data = data_overload
            projects.add(project)
            if project not in data[employee]:
                data[employee][project] = {}
            x_key = date
            data[employee][project][x_key] = forecast
        employees = list(employees)
        employees.sort()
        if _("Not assigned to an employee") in employees:
            # make sure it is the last one
            employees.remove(_("Not assigned to an employee"))
            employees.append(_("Not assigned to an employee"))
        projects = list(projects)
        projects.sort()
        for name in [_("Available"), _("Overload")]:
            if name in projects:
                # make sure these two get in the first tow positions
                projects.remove(name)
                projects.insert(0, name)
        return employees, projects, data_project, data_overload

    def _get_time_range(self):
        end_date = self.date_from + relativedelta(months=self.nb_months)
        dates = []
        granularity = self.granularity
        date = self.date_from
        delta = date_utils.get_timedelta(1, granularity)
        while date < end_date:
            dates.append(date.strftime("%Y-%m-%d"))
            date += delta
        return dates

    def _build_empty_plot(self, height=300, width=1024):
        dates = self._get_time_range()
        p = figure(height=height, width=width, x_range=FactorRange(*dates))
        p.title.text = _("Nothing to plot. Select some employees")
        return [p]

    def _get_palette(self, projects):
        """return a dictionary mapping project names to colors"""
        if len(projects) <= 20:
            project_colors = palettes.Category20[max(len(projects), 3)][: len(projects)]
        else:
            step = len(palettes.Turbo256) // len(projects)
            project_colors = palettes.Turbo256[::step][: len(projects)]
        return dict(zip(projects, project_colors))

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
